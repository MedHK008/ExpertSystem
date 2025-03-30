import json
from typing import List

def processDentisityForZones(service1_response: json) -> List[dict]:
    
    densities = [
        {"zoneId": zone["zoneId"], "density": zone["population"]}
        for zone in service1_response.get("zones", [])
        if zone["area_km2"] > 0
    ]
    
    results = [
        {"zoneId": item["zoneId"], **densite_appartient(item["density"])}
        for item in densities
    ]
    
    return results

def densite_appartient(densite):
    # Fonction d'appartenance trapézoïdale pour chaque catégorie de densité de population
    faible = max(0, min((500 - densite) / 500, 1)) if densite <= 500 else 0  # De 0 à 50 habitants/km²
    moyenne = max(0, min((densite - 500) / 1500, 1, (2000 - densite) / 1500))  # De 50 à 200 habitants/km²
    elevee = max(0, min((densite - 2000) / 3000, 1, (5000 - densite) / 3000))  # De 200 à 500 habitants/km²
    tres_elevee = max(0, min((densite - 5000) / 5000, 1)) if densite >= 5000 else 0  # Plus de 500 habitants/km²

    # Retourner les valeurs d'appartenance
    return {"faible": faible, "moyenne": moyenne, "elevee": elevee, "tres_elevee": tres_elevee}