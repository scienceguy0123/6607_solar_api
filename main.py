import csv
from apiKey import API_KEY
import requests
import json

url = "https://solar.googleapis.com/v1/buildingInsights:findClosest"


building_insights = []


def get_building_insights(latitude, longitude, quality="HIGH"):
    params = {
        "location.latitude": latitude,
        "location.longitude": longitude,
        "requiredQuality": quality,
        "key": API_KEY 
    }
    response = requests.get(url, params=params).json()

    building_insight = {
        "center_latitude" : response['center']['latitude'],
        "center_longitude" : response['center']['longitude'],
        "max_solar_count" : response['solarPotential']['solarPanelConfigs'][-1]['panelsCount'],
        "max_yearly_generation" : response['solarPotential']['solarPanelConfigs'][-1]['yearlyEnergyDcKwh'],
        "max_solar_array_size" :  response['solarPotential']['maxArrayAreaMeters2']
    }
    building_insights.append(building_insight)
    
    return response

with open("coor.csv", mode="r") as file:
    reader = csv.reader(file)
    next(reader)  # Skip the header
    for row in reader:
        get_building_insights(row[0], row[1])

        
with open("result.json", "w") as json_file:
    json.dump(building_insights, json_file, indent=4)
