import pandas as pd
import requests
import json
import time
import os
from tqdm import tqdm
try:
    from config import API_KEY, READ_SRC_CSV, WRITE_RESULT_CSV, WRITE_RESULT_JSON, SAVE_ORIGIN_RESPONSE, ORIGIN_RESPONSE_DIR, LATITUDE, LONGTIDUE, STORE_NAME, ADDRESS
except ImportError:
    print("Error: Can't find config.py file! Please ensure the config.py file exists and contains the necessary configuration information.")
    exit(1)

# Parameters
# URL for the Google Solar API
url = "https://solar.googleapis.com/v1/buildingInsights:findClosest"

# Global variables used to count the quality of rows
total_query_count = 0
high_quality_count = 0
medium_quality_count = 0
no_found_count = 0

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


# Process the CSV and extract building insights
def process():
    global total_query_count

    # Save each original response as a separate JSON file
    if SAVE_ORIGIN_RESPONSE:
        os.makedirs(ORIGIN_RESPONSE_DIR, exist_ok=True)

    # Read the CSV file using pandas
    df = pd.read_csv(READ_SRC_CSV)

    # Check if required columns exist
    required_columns = [LATITUDE, LONGTIDUE, STORE_NAME, ADDRESS]
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"The input file does not contain the required column: '{col}'.")

    # Add new columns for the extracted information
    df["center_latitude"] = None
    df["center_longitude"] = None
    df["max_solar_count"] = None
    df["max_yearly_generation"] = None
    df["max_solar_array_size"] = None

    # Create tqdm progress bar
    for index, row in tqdm(df.iterrows(), total=len(df), desc="Processing rows"):
        total_query_count += 1

        # Get building insights
        response, building_insight = get_building_insights(row[LATITUDE], row[LONGTIDUE])

        # Save the response in a JSON file if required
        if SAVE_ORIGIN_RESPONSE and response:
            # Extract storename and address
            storename = row.get(STORE_NAME, "unknown").replace(" ", "_").replace("/", "-")
            address = row.get(ADDRESS, "unknown").replace(" ", "_").replace("/", "-")
            # Construct the filename dynamically
            filename = f"{ORIGIN_RESPONSE_DIR}/{storename}_{address}.json"

            with open(filename, "w") as response_file:
                json.dump(response, response_file, indent=4)

        # Save extracted building insights to the DataFrame
        if building_insight:
            df.at[index, "center_latitude"] = building_insight["center_latitude"]
            df.at[index, "center_longitude"] = building_insight["center_longitude"]
            df.at[index, "max_solar_count"] = building_insight["max_solar_count"]
            df.at[index, "max_yearly_generation"] = building_insight["max_yearly_generation"]
            df.at[index, "max_solar_array_size"] = building_insight["max_solar_array_size"]

    # Save the updated DataFrame to a new CSV file
    df.to_csv(WRITE_RESULT_CSV, index=False)

    # Extract only relevant insights for saving to output JSON, ignoring rows with no insights
    subset_column = ["center_latitude", "center_longitude", "max_solar_count", "max_yearly_generation", "max_solar_array_size"]
    insights = df.dropna(subset=subset_column)
    insights_list = insights[subset_column].to_dict(orient="records")

    # Save the extracted building insights to a JSON file
    with open(WRITE_RESULT_JSON, "w") as json_file:
        json.dump(insights_list, json_file, indent=4)

    print(f"Processing completed! Results saved to {WRITE_RESULT_JSON} and {WRITE_RESULT_CSV}")


if __name__ == "__main__":
    # Start the timer
    start_time = time.time()

    # Process the CSV file and extract building insights
    process()

    # Print the total execution time
    end_time = time.time()
    print(f"Total execution time: {end_time - start_time:.2f} seconds")

    # Output the query result
    print(f"Total queries: {total_query_count}")
    print(f"High quality queries: {high_quality_count}")
    print(f"Medium quality queries: {medium_quality_count}")
    print(f"No response: {no_found_count}")
