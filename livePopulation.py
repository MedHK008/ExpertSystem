import json
from typing import List

def process_live_people(people_data: json) -> List[dict]:
        
        processed_data = []
        for zone in people_data:
            zoneId = zone["zoneId"]
            totals = zone["totals"]
            nb_personnes = totals["person"]
            
            personnes_appartenance = personnes_appartient(nb_personnes)
            
            processed_data.append({
                "zoneId": zoneId,
                "people": nb_personnes,
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
    return {"faible": faible, "moyenne": moyenne, "elevee": elevee, "tres_elevee": tres_elevee}