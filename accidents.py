import json
from typing import List

def process_zone_accident(data: json) -> List[dict]:
    accidents = [
        {
            "zoneId": accident["zoneId"],
            "accidents": accident["accidents"]
        }
        for accident in data.get("zones", [])
        if accident["accidents"] > 0
    ]
    results = [
        {
            "zoneId": item["zoneId"],
            "accidents": accidents_appartient(item["accidents"])
        }
        for item in accidents
    ]
    return results

def accidents_appartient(nb_accidents):
    # Fonction d'appartenance trapézoïdale pour chaque catégorie de nombre d'accidents
    faible = max(0, min((10 - nb_accidents) / 10, 1)) if nb_accidents <= 10 else 0  # De 0 à 10 accidents
    moyenne = max(0, min((nb_accidents - 5) / 25, 1, (30 - nb_accidents) / 25))  # De 5 à 30 accidents
    elevee = max(0, min((nb_accidents - 20) / 30, 1, (50 - nb_accidents) / 30))  # De 20 à 50 accidents
    tres_elevee = max(0, min((nb_accidents - 50) / 50, 1)) if nb_accidents >= 50 else 0  # Plus de 50 accidents

    # Retourner les valeurs d'appartenance
    return {"Faible": faible, "Moyen": moyenne, "elevee": elevee, "tres_elevee": tres_elevee}