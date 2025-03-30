def preprocess_data(data):
    result = []
    # Preprocess weather data once as it's the same for all zones
    weather_entry = data["weather"][0]
    max_wind = max(weather_entry["appartenance_wind"], key=lambda k: weather_entry["appartenance_wind"][k])
    max_rain = max(weather_entry["appartenance_rain"], key=lambda k: weather_entry["appartenance_rain"][k])
    max_snow = max(weather_entry["appartenance_snow"], key=lambda k: weather_entry["appartenance_snow"][k])
    
    for zone in data["population"]:
        zone_id = zone["zoneId"]
        
        # Process population
        pop_keys = [k for k in zone if k != "zoneId"]
        max_population = max(pop_keys, key=lambda k: zone[k])
        
        # Process traffic
        traffic_entry = next(t for t in data["traffic"] if t["zoneId"] == zone_id)
        max_traffic = max(traffic_entry["appartenance"], key=lambda k: traffic_entry["appartenance"][k])
        
        # Process people
        people_entry = next(p for p in data["people"] if p["zoneId"] == zone_id)
        max_people = max(people_entry["appartenance"], key=lambda k: people_entry["appartenance"][k])
        
        # Process zone_risc
        risc_entry = next(r for r in data["zone_risc"] if r["zoneId"] == zone_id)
        max_riscP = max(risc_entry["riscP"], key=lambda k: risc_entry["riscP"][k])
        max_riscC = max(risc_entry["riscC"], key=lambda k: risc_entry["riscC"][k])
        
        # Process accidents
        accident_entry = next(a for a in data["accidents"] if a["zoneId"] == zone_id)
        max_accident = max(accident_entry["accidents"], key=lambda k: accident_entry["accidents"][k])
        
        result.append({
            "zoneId": zone_id,
            "population": max_population,
            "traffic": max_traffic,
            "people": max_people,
            "zone_risc_riscP": max_riscP,
            "zone_risc_riscC": max_riscC,
            "weather_appartenance_wind": max_wind,
            "weather_appartenance_rain": max_rain,
            "weather_appartenance_snow": max_snow,
            "accidents": max_accident
        })
    return result