import json
import math
from typing import List

km_per_deg_lat = 111.32 

def calculate_density(cameras: dict) -> dict:
    # Dictionary to store the area for each camera
    camera_areas = {}
    
    # Iterate over the values of the cameras dictionary
    for camera_id, camera_data in cameras.items():
        coverage = camera_data["coverage_area"]
        lat_diff = coverage[1][0] - coverage[0][0]
        lon_diff = coverage[1][1] - coverage[0][1]
        mean_lat = (coverage[0][0] + coverage[1][0]) / 2.0
        km_per_deg_lon = 111.32 * math.cos(math.radians(mean_lat))
        # Convert degree differences to kilometers
        lat_distance_km = lat_diff * km_per_deg_lat
        lon_distance_km = lon_diff * km_per_deg_lon
        # Calculate the area in square kilometers
        area_km2 = lat_distance_km * lon_distance_km
        # Store the area in the dictionary
        camera_areas[camera_id] = area_km2
    
    return camera_areas

def process_live_people(people_data: json) -> List[dict]:
        
        processed_data = []
        for zone in people_data:
            zoneId = zone["zoneId"]
            totals = zone["totals"]
            nb_personnes = totals.get("personnes", 20)
            cameras = zone["cameras"]
            areas = calculate_density(cameras)
            total_area = sum(areas.values())
            density = nb_personnes / total_area if total_area > 0 else 0
            personnes_appartenance = personnes_appartient(density)
            processed_data.append({
                "zoneId": zoneId,
                "live_density": nb_personnes,
                "appartenance": personnes_appartenance
            })
        
        return processed_data



def personnes_appartient(nb_personnes):
    # Fonction d'appartenance trapézoïdale pour chaque catégorie de nombre de personnes (par seconde)
    faible = max(0, min((1 - nb_personnes) / 1, 1)) if nb_personnes <= 1 else 0  # De 0 à 1 personne/seconde
    moyenne = max(0, min((nb_personnes - 1) / 2, 1, (3 - nb_personnes) / 2))  # De 1 à 3 personnes/seconde
    elevee = max(0, min((nb_personnes - 3) / 4, 1, (7 - nb_personnes) / 4))  # De 3 à 7 personnes/seconde
    tres_elevee = max(0, min((nb_personnes - 7) / 3, 1)) if nb_personnes >= 7 else 0  # Plus de 7 personnes/seconde

    # Retourner les valeurs d'appartenance
    return {"Faible": faible, "Moyen": moyenne, "elevee": elevee, "tres_elevee": tres_elevee}