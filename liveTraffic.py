import json
from typing import List
def process_traffic_data(traffic_data:json) -> List[dict]:
    processed_data = []
    for zone in traffic_data:
        zoneId = zone["zoneId"]
        totals = zone["totals"]
        
        # Use .get() with default value 0 to handle missing keys
        nb_vehicules = totals.get("car", 0) + totals.get("truck", 0) + totals.get("bus", 0) + totals.get("motorcycle", 0) 
        
        trafic_appartenance = trafic_appartient(nb_vehicules)
        
        processed_data.append({
            "zoneId": zoneId,
            "traffic": nb_vehicules,
            "appartenance": trafic_appartenance
        })
    
    return processed_data

def trafic_appartient(nb_vehicules):
    faible = max(0, min((5 - nb_vehicules) / 5, 5)) if nb_vehicules <= 1 else 0
    moyenne = max(0, min((nb_vehicules - 1) / 12, 1, (10 - nb_vehicules) / 12))
    elevee = max(0, min((nb_vehicules - 12) / 18, 1, (25 - nb_vehicules) / 18))
    tres_elevee = max(0, min((nb_vehicules - 25) / 25, 1)) if nb_vehicules >= 25 else 0

    # Retourner les valeurs d'appartenance
    return {"Faible": faible, "Moyen": moyenne, "elevee": elevee, "tres_elevee": tres_elevee}


