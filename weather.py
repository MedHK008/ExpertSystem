import json
from typing import List

def process_weather_data(weather_data: json) -> List[dict]:
    processed_data = []
    
    wind_speed = weather_data["windSpeed"]
    precipitation = weather_data["precipitation"]
    rain = precipitation["rain"]
    snow = precipitation["snow"]

    appartenance_vitesse = vent_appartient(wind_speed)
    appartenance_rain = rain_appartient(rain)
    appartenance_snow = snow_appartient(snow)

    processed_data.append({
        "wind_speed": wind_speed,
        "precipitation": precipitation,
        "appartenance_wind": appartenance_vitesse,
        "appartenance_rain": appartenance_rain,
        "appartenance_snow": appartenance_snow
    })

    return processed_data

def vent_appartient(vitesse):
    # Fonction d'appartenance trapézoïdale pour chaque catégorie de vitesse du vent
    faible = max(0, min((20 - vitesse) / 20, 1)) if vitesse <= 20 else 0  # De 0 km/h à 20 km/h
    moyenne = max(0, min((vitesse - 10) / 20, 1, (40 - vitesse) / 20))  # De 10 km/h à 40 km/h
    elevee = max(0, min((vitesse - 30) / 30, 1, (60 - vitesse) / 30))  # De 30 km/h à 60 km/h
    return {"Faible": faible, "Moyen": moyenne, "elevee": elevee}

def rain_appartient(precipitation):
    # Fonction d'appartenance trapézoïdale pour chaque catégorie de précipitation
    faible = max(0, min((5 - precipitation) / 5, 1)) if precipitation <= 5 else 0  # De 0 mm/h à 5 mm/h
    moderee = max(0, min((precipitation - 3) / 6, 1, (15 - precipitation) / 12))  # De 3 mm/h à 15 mm/h
    elevee = max(0, min((precipitation - 10) / 20, 1, (30 - precipitation) / 20))  # De 10 mm/h à 30 mm/h
    return {"Faible": faible, "Moyen": moderee, "elevee": elevee}

def snow_appartient(snow_rate):
    # Fonction d'appartenance trapézoïdale pour chaque catégorie de neige (en mm/h)
    none = 1 if snow_rate == 0 else max(0, min((2 - snow_rate) / 2, 1))
    faible = max(0, min((snow_rate - 0) / 2, 1, (5 - snow_rate) / 3))
    moyenne = max(0, min((snow_rate - 2) / 3, 1, (10 - snow_rate) / 5))
    elevee = max(0, min((snow_rate - 5) / 5, 1)) if snow_rate >= 5 else 0

    # Retourner les valeurs d'appartenance
    return {
        "None": none,
        "Faible": faible,
        "Moyen": moyenne,
        "elevee": elevee
    }