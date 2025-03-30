from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import httpx
from population import processDentisityForZones
from liveTraffic import process_traffic_data
from livePopulation import process_live_people
from zoneRisc import processZoneRisc
from weather import process_weather_data
from accidents import process_zone_accident
from inferenceSystem import preprocess_data

app = FastAPI()


class ZoneIds(BaseModel):
    zone_ids: List[str]

@app.post("/zone_ids")
async def receive_zone_ids(zone_ids: ZoneIds):
    print("received_zone_ids", zone_ids.zone_ids)

    # first service, get the population of the zones
    async with httpx.AsyncClient() as client:
        response = await client.post("http://127.0.0.1:8000/zones", json={"zone_ids": zone_ids.zone_ids})
        response_data = response.json()
    population = processDentisityForZones(response_data)
    
    # second service, get the live data of the zones
    live_data = []
    for zone in zone_ids.zone_ids :
        async with httpx.AsyncClient() as client:
            response = await client.post("http://127.0.0.1:9000/get_live_data", json={"zoneId": zone})
            response_data = response.json()
        live_data.append({
            "zoneId": response_data["zoneId"],
            "totals": response_data["totals"]
        })
    traffic = process_traffic_data(live_data)
    people = process_live_people(live_data)
    
    
    # third service, get the risk of the zones
    json_data = {
        "zones": [
            {"zoneId": zone}
            for zone in zone_ids.zone_ids
        ]
    }
    async with httpx.AsyncClient() as client:
        response = await client.post("http://localhost:8085/api/buildingRisc/risc", json=json_data)
        response_data = response.json()
    filtered_data = [
        {
            "zoneId": zone["zoneId"],
            "riscP": zone["riscP"],
            "riscC": zone["riscC"]
        }
        for zone in response_data.get("anotherzones", [])
    ]
    zone_risc = processZoneRisc(filtered_data)
    
    # fourth service, get the weather data
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8090/api/weather")
        response_data = response.json()
    weather = process_weather_data(response_data)
    
    # fifth service, get the accidents data
    async with httpx.AsyncClient() as client:
        response = await client.post("http://127.0.0.1:8009/accidents_per_zone", json={"zone_ids": zone_ids.zone_ids})
        response_data = response.json()
    # print("accidents_data", response_data)
    accidents = process_zone_accident(response_data)
    # print("accidents", accidents)
    
    
    aggregated_data = {
        "population": population,
        "traffic": traffic,
        "people": people,
        "zone_risc": zone_risc,
        "weather": weather,
        "accidents": accidents
    }
    # print("aggregated_data", aggregated_data)
    data = preprocess_data(aggregated_data)
    return {"data": data}
