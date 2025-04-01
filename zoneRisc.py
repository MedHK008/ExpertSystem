import json
from typing import List

def processZoneRisc(zone_data: json) -> List[dict]:
    processed_data = []
    for zone in zone_data:
        zoneId = zone["zoneId"]
        riscP = zone["riscP"]
        riscC = zone["riscC"]

        # Calculer l'appartenance pour le risque de la population et du trafic
        appartenance_population = risque_appartient(riscP)
        appartenance_trafic = risque_appartient(riscC)

        processed_data.append({
            "zoneId": zoneId,
            "riscP": appartenance_population,
            "riscC": appartenance_trafic
        })

    return processed_data

def risque_appartient(risque):
    # Handle None values
    if risque is None:
        return {"aucun": 0, "Faible": 0, "Moyen": 0, "elevee": 0}

    # Fonction d'appartenance trapézoïdale pour chaque catégorie de risque
    aucun = max(0, min((0.10 - risque) / 0.10, 1)) if risque <= 0.10 else 0  # De 0 à 0.15
    faible = max(0, min((risque - 0.10) / 0.2, 1, (0.35 - risque) / 0.2))  # De 0.15 à 0.35
    moyenne = max(0, min((risque - 0.35) / 0.4, 1, (0.75 - risque) / 0.4))  # De 0.35 à 0.75
    eleve = max(0, min((risque - 0.75) / 0.25, 1)) if risque >= 0.75 else 0  # De 0.75 à 1

    # Retourner les valeurs d'appartenance
    return {"aucun": aucun, "Faible": faible, "Moyen": moyenne, "elevee": eleve}