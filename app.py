import os
import re
import streamlit as st
from PIL import Image
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

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
# Load data
# ---------------------------------------------------------
@st.cache_data
def get_plants():
    plants = load_all_plants()
    plants = dedupe_plants(plants)
    return plants


plants = get_plants()


# ---------------------------------------------------------
# Page layout
# ---------------------------------------------------------
st.set_page_config(page_title="Plant Safety Checker", layout="wide")
st.title("Plant Safety Checker 🌿")

left, right = st.columns([1, 1.2])


# ---------------------------------------------------------
# LEFT SIDE — Search + Filter + Table
# ---------------------------------------------------------
with left:
    st.subheader("Search & Filter")

    # Toxicity filter
    filter_choice = st.selectbox("Filter by toxicity", ["All", "Toxic", "Safe"])

    # Search box
    query = st.text_input("Search plants")

    # Apply filters
    filtered = []
    q = query.lower()

    for plant in plants:
        if filter_choice == "Toxic" and not plant["toxic"]:
            continue
        if filter_choice == "Safe" and plant["toxic"]:
            continue

        searchable = " ".join([
            plant["name"],
            plant["other"],
            plant["scientific"],
            plant["family"],
            "toxic" if plant["toxic"] else "safe"
        ]).lower()

        if q in searchable:
            filtered.append({
                "Name": plant["name"],
                "Scientific": plant["scientific"],
                "Family": plant["family"],
                "Toxicity": "Toxic" if plant["toxic"] else "Safe"
            })

    st.write(f"Showing {len(filtered)} plants")

    # Build AgGrid table
    import pandas as pd

    df = pd.DataFrame(filtered)
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_selection("single")
    gb.configure_column("Name", sortable=True, resizable=True)
    gb.configure_column("Scientific", sortable=True, resizable=True)
    gb.configure_column("Family", sortable=True, resizable=True)
    gb.configure_column("Toxicity", sortable=True, resizable=True)

    grid_options = gb.build()

    grid_response = AgGrid(
        filtered,
        gridOptions=grid_options,
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        height=600,
        fit_columns_on_grid_load=True
    )

    selected = grid_response["selected_rows"]


# ---------------------------------------------------------
# RIGHT SIDE — Details + Image
# ---------------------------------------------------------
with right:
    st.subheader("Details & Image")

    if not selected:
        st.info("Click a plant in the table to view details.")
    else:
        row = selected[0]
        name = row["Name"]

        # Find the original plant object
        plant = next(p for p in plants if p["name"] == name)

        st.markdown(f"### {plant['name']}")
        st.markdown(f"**Scientific name:** {plant['scientific']}")
        st.markdown(f"**Family:** {plant['family']}")
        st.markdown(f"**Other names:** {plant['other'] or '—'}")

        tox_label = "Toxic to cats" if plant["toxic"] else "Non-toxic to cats"
        tox_color = "red" if plant["toxic"] else "green"
        st.markdown(f"**Toxicity:** <span style='color:{tox_color}'>{tox_label}</span>", unsafe_allow_html=True)

        img_path = find_image(plant["name"])

        if img_path:
            st.image(img_path, use_column_width=True)
        else:
            st.warning("No image available for this plant.")