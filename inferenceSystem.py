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
        traffic_entry = next(t for t in data["traffic"] if t["zoneId"] == zone_id)
        max_traffic = max(traffic_entry["appartenance"], key=lambda k: traffic_entry["appartenance"][k])
        
        # Process people
        people_entry = next(p for p in data["live_density"] if p["zoneId"] == zone_id)
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
            return all(evaluate_condition(item, fact) for item in items)
        elif operator == "OR":
            return any(evaluate_condition(item, fact) for item in items)
    else:
        variable = condition["variable"]
        value = condition["value"]
        return fact.get(variable) == value

def infer_risk(processed_fact):
    triggered_risks = []
    for rule in rules_collection.find():
        if evaluate_condition(rule["conditions"], processed_fact):
            triggered_risks.append(rule["conclusion"]["Risque"])
    
    risk_order = ["Élevé", "Moyen", "Faible"]
    for risk in risk_order:
        if risk in triggered_risks:
            return risk
    return "None"

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