# plant_loader.py

def load_all_plants():
    plants = []

    # Toxic plants
    with open("plants_toxic_to_cats.txt", "r", encoding="utf-8") as f:
        for line in f:
            parts = [p.strip() for p in line.split("|")]
            if len(parts) == 4:
                plants.append({
                    "name": parts[0],
                    "other": parts[1],
                    "scientific": parts[2],
                    "family": parts[3],
                    "toxic": True
                })

    # Non-toxic plants
    with open("plants_nontoxic_to_cats.txt", "r", encoding="utf-8") as f:
        for line in f:
            parts = [p.strip() for p in line.split("|")]
            if len(parts) == 4:
                plants.append({
                    "name": parts[0],
                    "other": parts[1],
                    "scientific": parts[2],
                    "family": parts[3],
                    "toxic": False
                })

    return plants


def dedupe_plants(plants):
    seen = set()
    unique = []

    for plant in plants:
        key = plant["name"].lower()
        if key not in seen:
            seen.add(key)
            unique.append(plant)

    return unique