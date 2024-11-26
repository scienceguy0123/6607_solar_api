import csv
import requests
import json
import time
import os

# Macro
# Define whether save original responses
SAVE_ORIGIN_RESPONSE = True

# Parameters
# URL for the Google Solar API
url = "https://solar.googleapis.com/v1/buildingInsights:findClosest"
# The file storing API key
api_key_file = "mysolarApi.txt"

# Read CSV file and write JSON file
read_src_csv = "../data-school/split_data_6.csv"
write_result_json = "result_split_data_6.json"
# Extract attributes
column_longitude = "LONGITUDE"
column_latitude = "LATITUDE"
# Diectory of saving original responses
if SAVE_ORIGIN_RESPONSE:
    origin_response_dir = "origin_response_split_data_6"

# Global variables used to count the quality of rows
total_query_count = 0
high_quality_count = 0
medium_quality_count = 0
no_found_count = 0

# Read the API key from 'mysolarApi.txt'
def get_api_key(file_path):
    try:
        with open(file_path, 'r') as file:
            return file.read().strip()  # Read and remove any extra whitespace or newlines
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' does not exist.")
        return None
    except Exception as e:
        print(f"An error occurred while reading the API key: {e}")
        return None

# Get and extract required attributes from API response
def get_building_insights(latitude, longitude, quality="HIGH"):
    global high_quality_count, medium_quality_count, no_found_count

    params = {
        "location.latitude": latitude,
        "location.longitude": longitude,
        "requiredQuality": quality,
        "key": API_KEY
    }

    try:
        response = requests.get(url, params=params).json()

        # Check for error in the response
        if "error" in response:
            if response["error"]["status"] == "NOT_FOUND" and quality == "HIGH":
                return get_building_insights(latitude, longitude, quality="MEDIUM")
            else:
                print(f"Error for ({latitude}, {longitude}): {response['error']['message']}")
                no_found_count += 1
                return response, None
        
        # Count the response quality
        if quality == "HIGH":
            high_quality_count += 1
        if quality == "MEDIUM":
            medium_quality_count += 1

        # Extract relevant information for summary
        building_insight = {
            "center_latitude": response['center']['latitude'],
            "center_longitude": response['center']['longitude'],
            "max_solar_count": response['solarPotential']['solarPanelConfigs'][-1]['panelsCount'],
            "max_yearly_generation": response['solarPotential']['solarPanelConfigs'][-1]['yearlyEnergyDcKwh'],
            "max_solar_array_size": response['solarPotential']['maxArrayAreaMeters2']
        }

        return response, building_insight

    except Exception as e:
        print(f"An unexpected error occurred for ({latitude}, {longitude}): {e}")
        no_found_count += 1
        return None, None

if __name__ == "__main__":
    # Start the timer
    start_time = time.time()

    # Get the API key from the text file
    API_KEY = get_api_key(api_key_file)
    if API_KEY is None:
        print("API key could not be loaded. Exiting...")
        exit()

    # Create the directory for saving original responses
    if SAVE_ORIGIN_RESPONSE:
        os.makedirs(origin_response_dir, exist_ok=True)

    # Store the building insights
    building_insights = []

    # Read coordinates from a CSV file
    with open(read_src_csv, mode="r") as file:
        reader = csv.reader(file)
        header = next(reader)  # Read the header row
        longitude_index = header.index(column_longitude)  # Find the index of "LONGITUDE"
        latitude_index = header.index(column_latitude)    # Find the index of "LATITUDE"

        for row_index, row in enumerate(reader):
            # Total query count accumulates
            total_query_count += 1

            response, building_insight = get_building_insights(row[latitude_index], row[longitude_index])

            # Save each original response as a separate JSON file
            if SAVE_ORIGIN_RESPONSE and response:
                with open(f"{origin_response_dir}/response_{row_index}.json", "w") as response_file:
                    json.dump(response, response_file, indent=4)

            # Save extracted building insights
            if building_insight:
                building_insights.append(building_insight)

    # Save summarized results to a JSON file
    with open(write_result_json, "w") as json_file:
        json.dump(building_insights, json_file, indent=4)

    # Print the total execution time
    end_time = time.time()
    print(f"Total execution time: {end_time - start_time:.2f} seconds")

    # Output the query result
    print(f"Total queries: {total_query_count}")
    print(f"High quality queries: {high_quality_count}")
    print(f"Medium quality queries: {medium_quality_count}")
    print(f"No response: {no_found_count}")
