from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["geofencingDB"]
rules_collection = db["rules"]

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
        traffic_entry = next((t for t in data["traffic"] if t["zoneId"] == zone_id), None)
        max_traffic = max(traffic_entry["appartenance"], key=lambda k: traffic_entry["appartenance"][k]) if traffic_entry else "None"
        
        # Process people
        people_entry = next((p for p in data["live_density"] if p["zoneId"] == zone_id), None)
        max_people = max(people_entry["appartenance"], key=lambda k: people_entry["appartenance"][k]) if people_entry else "None"
        
        # Process zone_risc
        risc_entry = next((r for r in data["zone_risc"] if r["zoneId"] == zone_id), None)
        max_riscP = max(risc_entry["riscP"], key=lambda k: risc_entry["riscP"][k]) if risc_entry else "None"
        max_riscC = max(risc_entry["riscC"], key=lambda k: risc_entry["riscC"][k]) if risc_entry else "None"
        
        # Process accidents
        accident_entry = next((a for a in data["accidents"] if a["zoneId"] == zone_id), None)
        max_accident = max(accident_entry["accidents"], key=lambda k: accident_entry["accidents"][k]) if accident_entry else "None"
        
        result.append({
            "zoneId": zone_id,
            "population": max_population,
            "traffic": max_traffic,
            "liveDensity": max_people,
            "sensibilityP": max_riscP,
            "sensibilityC": max_riscC,
            "Vent": max_wind,
            "Rain": max_rain,
            "Snow": max_snow,
            "Accidents": max_accident
        })
    return result

def preprocess_fact(fact):
    variable_mapping = {
        "population": "population",
        "traffic": "Traffic",
        "liveDensity": "liveDensity",
        "sensibilityP": "sensibilityP",
        "sensibilityC": "sensibilityC",
        "Vent": "Vent",
        "Rain": "Rain",
        "Snow": "Snow",
        "Accidents": "Accidents"
    }
    
    value_mapping = {
        "tres_elevee": "Élevé",
        "elevee": "Élevé",
        "moyenne": "Moyen",
        "faible": "Faible",
        "None": None
    }
    
    processed = {}
    for fact_key, fact_value in fact.items():
        if fact_key in variable_mapping:
            rule_var = variable_mapping[fact_key]
            mapped_value = value_mapping.get(fact_value, fact_value)
            processed[rule_var] = mapped_value
    return processed

def evaluate_condition(condition, fact):
    if "operator" in condition:
        operator = condition["operator"]
        items = condition["items"]
        if operator == "AND":
            results = [evaluate_condition(item, fact) for item in items]
            # if not all(results):
            #     print(f"Condition failed (AND): {items} with results {results}")
            return all(results)
        elif operator == "OR":
            results = [evaluate_condition(item, fact) for item in items]
            # if not any(results):
                # continue
                # print(f"Condition failed (OR): {items} with results {results}")
            return any(results)
    else:
        variable = condition["variable"]
        value = condition["value"]
        result = fact.get(variable) == value
        # if not result:
            # continue
            # print(f"Condition failed: Variable '{variable}' expected '{value}', got '{fact.get(variable)}'")
        return result

def infer_risk(processed_fact):
    triggered_risks = []
    for rule in rules_collection.find():
        # print(f"Evaluating rule: {rule['rule_number']}")
        if evaluate_condition(rule["conditions"], processed_fact):
            # print(f"Rule triggered: {rule['rule_number']}")
            triggered_risks.append(rule["conclusion"]["Risque"])
        else:
            continue
            # print(f"Rule not triggered: {rule['rule_number']}")
    
    risk_order = ["Élevé", "Moyen", "Faible"]
    for risk in risk_order:
        if risk in triggered_risks:
            return risk
    return "Faible"  # Default risk if none triggered

def infer_risk_from_facts(facts):
    results = []
    for fact in facts:
        processed_fact = preprocess_fact(fact)
        risk = infer_risk(processed_fact)
        results.append({
            "zoneId": fact["zoneId"],
            "risk": risk
        })
    return results