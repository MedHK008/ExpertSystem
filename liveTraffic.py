import json
from typing import List
def process_traffic_data(traffic_data:json) -> List[dict]:
    processed_data = []
    for zone in traffic_data:
        zoneId = zone["zoneId"]
        totals = zone["totals"]
        
        nb_vehicules = totals["car"] + totals["truck"] + totals["bus"] + totals["motorcycle"]
        
        trafic_appartenance = trafic_appartient(nb_vehicules)
        
        processed_data.append({
            "zoneId": zoneId,
            "traffic": nb_vehicules,
            "appartenance": trafic_appartenance
        })
    
    return processed_data

def trafic_appartient(nb_vehicules):
    faible = max(0, min((1 - nb_vehicules) / 1, 1)) if nb_vehicules <= 1 else 0
    moyenne = max(0, min((nb_vehicules - 1) / 6, 1, (8 - nb_vehicules) / 6))
    elevee = max(0, min((nb_vehicules - 6) / 10, 1, (14 - nb_vehicules) / 10))
    tres_elevee = max(0, min((nb_vehicules - 14) / 14, 1)) if nb_vehicules >= 14 else 0

    # Retourner les valeurs d'appartenance
    return {"Faible": faible, "Moyen": moyenne, "elevee": elevee, "tres_elevee": tres_elevee}


