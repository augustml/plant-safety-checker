import os
import re

import streamlit as st
from PIL import Image

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
# Load data (cached for performance)
# ---------------------------------------------------------
@st.cache_data
def get_plants():
    plants = load_all_plants()
    plants = dedupe_plants(plants)
    return plants


plants = get_plants()


# ---------------------------------------------------------
# Layout
# ---------------------------------------------------------
st.set_page_config(page_title="Plant Safety Checker", layout="wide")

st.title("Plant Safety Checker 🌿")

col_left, col_right = st.columns([1, 1.2])


# ---------------------------------------------------------
# Left side: filters + table
# ---------------------------------------------------------
with col_left:
    st.subheader("Search & Filter")

    # Toxicity filter
    filter_choice = st.selectbox(
        "Filter by toxicity",
        ["All", "Toxic", "Safe"],
        index=0
    )

    # Search box
    query = st.text_input("Search (name, scientific, family, etc.)", "")

    # Filter + search
    filtered = []
    q = query.lower()

    for plant in plants:
        # Toxicity filter
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

        if q in searchable:
            filtered.append(plant)

    # Build a simple table-like view
    st.write(f"Showing {len(filtered)} plants")

    # Let user select a plant
    names = [f"{p['name']} ({p['scientific']})" for p in filtered]
    selected_label = st.selectbox(
        "Select a plant",
        ["(none)"] + names
    )

    selected_plant = None
    if selected_label != "(none)":
        idx = names.index(selected_label)
        selected_plant = filtered[idx]


# ---------------------------------------------------------
# Right side: details + image
# ---------------------------------------------------------
with col_right:
    st.subheader("Details & Image")

    if selected_plant is None:
        st.info("Select a plant from the left to see details and image.")
    else:
        # Text details
        st.markdown(f"### {selected_plant['name']}")
        st.markdown(f"**Scientific name:** {selected_plant['scientific']}")
        st.markdown(f"**Family:** {selected_plant['family']}")
        st.markdown(f"**Other names:** {selected_plant['other'] or '—'}")

        tox_label = "Toxic to cats" if selected_plant["toxic"] else "Non-toxic to cats"
        tox_color = "red" if selected_plant["toxic"] else "green"
        st.markdown(f"**Toxicity:** <span style='color:{tox_color}'>{tox_label}</span>", unsafe_allow_html=True)

        # Image
        img_path = find_image(selected_plant["name"])

        if img_path:
            img = Image.open(img_path)
            # Streamlit handles resizing nicely; you can control width
            st.image(img, caption=selected_plant["name"], use_column_width=True)
        else:
            st.warning("No image available for this plant.")