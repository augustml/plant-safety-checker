import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
import re

from plant_loader import load_all_plants, dedupe_plants


# ---------------------------------------------------------
# Utility: find image file based on plant name
# ---------------------------------------------------------
def find_image(plant_name):
    base = plant_name.split("(")[0].strip()
    safe = base.lower()
    safe = re.sub(r"[^a-z0-9 ]", "", safe)
    safe = safe.replace(" ", "_")

    image_folder = "images"
    for ext in ["jpg", "jpeg", "png", "webp"]:
        path = os.path.join(image_folder, f"{safe}.{ext}")
        if os.path.exists(path):
            return path

    return None


# ---------------------------------------------------------
# Display image when a plant is selected
# ---------------------------------------------------------
def show_image(event):
    selected = results.focus()
    if not selected:
        return

    values = results.item(selected, "values")
    plant_name = values[0]

    img_path = find_image(plant_name)

    if not img_path:
        img_label.config(image="", text="No image available")
        return

    img = Image.open(img_path)

    # High-quality resize
    max_width = 600
    max_height = 600
    img.thumbnail((max_width, max_height), Image.LANCZOS)

    img_tk = ImageTk.PhotoImage(img)
    img_label.image = img_tk
    img_label.config(image=img_tk, text="")


# ---------------------------------------------------------
# Sorting logic for Treeview columns
# ---------------------------------------------------------
def sort_column(tree, col, reverse):
    data = [(tree.set(child, col), child) for child in tree.get_children("")]
    data.sort(reverse=reverse)

    for index, (val, child) in enumerate(data):
        tree.move(child, "", index)

    tree.heading(col, command=lambda: sort_column(tree, col, not reverse))


# ---------------------------------------------------------
# Search + filter logic
# ---------------------------------------------------------
def update_search(*args):
    query = search_var.get().lower()
    filter_choice = filter_var.get()

    results.delete(*results.get_children())

    for plant in plants:
        # Apply toxicity filter
        if filter_choice == "Toxic" and not plant["toxic"]:
            continue
        if filter_choice == "Safe" and plant["toxic"]:
            continue

        # Search across all fields
        searchable = " ".join([
            plant["name"],
            plant["other"],
            plant["scientific"],
            plant["family"],
            "toxic" if plant["toxic"] else "safe"
        ]).lower()

        if query in searchable:
            tag = "toxic" if plant["toxic"] else "safe"
            results.insert(
                "",
                "end",
                values=(
                    plant["name"],
                    plant["scientific"],
                    plant["family"],
                    "Toxic" if plant["toxic"] else "Safe"
                ),
                tags=(tag,)
            )


# ---------------------------------------------------------
# Clear search
# ---------------------------------------------------------
def clear_search():
    search_var.set("")
    filter_var.set("All")
    update_search()


# ---------------------------------------------------------
# GUI Setup
# ---------------------------------------------------------
root = tk.Tk()
root.title("Plant Safety Checker")
root.geometry("1600x950")

# Left panel
left_frame = tk.Frame(root)
left_frame.pack(side="left", fill="y", padx=20, pady=20)

# Right panel (image display)
image_frame = tk.Frame(root, width=600, height=600)
image_frame.pack(side="right", fill="both", expand=True)

img_label = tk.Label(image_frame, text="Select a plant to view image")
img_label.pack(expand=True)


# ---------------------------------------------------------
# Load plant data
# ---------------------------------------------------------
plants = load_all_plants()
plants = dedupe_plants(plants)


# ---------------------------------------------------------
# Dropdown filter (Toxic / Safe / All)
# ---------------------------------------------------------
filter_var = tk.StringVar(value="All")

filter_dropdown = ttk.Combobox(
    left_frame,
    textvariable=filter_var,
    values=["All", "Toxic", "Safe"],
    state="readonly",
    width=20
)
filter_dropdown.pack(pady=10)


# ---------------------------------------------------------
# Search bar + Clear button
# ---------------------------------------------------------
search_var = tk.StringVar()
search_var.trace("w", update_search)
filter_var.trace("w", update_search)

search_entry = tk.Entry(left_frame, textvariable=search_var, width=40)
search_entry.pack(pady=5)

clear_button = tk.Button(left_frame, text="Clear Search", command=clear_search)
clear_button.pack(pady=5)


# ---------------------------------------------------------
# Table of plants (with scrollbars + column resizing)
# ---------------------------------------------------------
table_frame = tk.Frame(left_frame)
table_frame.pack(fill="both", expand=True)

# Scrollbars
scroll_y = tk.Scrollbar(table_frame, orient="vertical")
scroll_x = tk.Scrollbar(table_frame, orient="horizontal")

columns = ("Name", "Scientific", "Family", "Toxicity")
results = ttk.Treeview(
    table_frame,
    columns=columns,
    show="headings",
    height=35,
    yscrollcommand=scroll_y.set,
    xscrollcommand=scroll_x.set
)

scroll_y.config(command=results.yview)
scroll_x.config(command=results.xview)

scroll_y.pack(side="right", fill="y")
scroll_x.pack(side="bottom", fill="x")
results.pack(fill="both", expand=True)

# Column setup with sorting + resizing
for col in columns:
    results.heading(col, text=col, command=lambda c=col: sort_column(results, c, False))
    results.column(col, width=200, anchor="w")

# Color coding
results.tag_configure("toxic", background="#ffcccc")
results.tag_configure("safe", background="#ccffcc")

# Populate table
for plant in plants:
    tag = "toxic" if plant["toxic"] else "safe"
    results.insert(
        "",
        "end",
        values=(
            plant["name"],
            plant["scientific"],
            plant["family"],
            "Toxic" if plant["toxic"] else "Safe"
        ),
        tags=(tag,)
    )

# Bind selection
results.bind("<<TreeviewSelect>>", show_image)


root.mainloop()