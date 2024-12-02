import pandas as pd
import requests
import json
import os
from tqdm import tqdm
try:
    from config import API_KEY, READ_SRC_CSV, WRITE_RESULT_CSV_DATA_VERIF,WRITE_RESULT_CSV_OUTPUT_VERIF, \
        WRITE_RESULT_JSON, SAVE_ORIGIN_RESPONSE, ORIGIN_RESPONSE_DIR, LATITUDE, LONGTIDUE, STORE_NAME, ADDRESS, \
            LAT_LNG_THRESHOLD, MIN_PANELS, MAX_PANELS
except ImportError:
    print("Error: Can't find config.py file! Please ensure the config.py file exists and contains the necessary configuration information.")
    exit(1)

# Parameters
# URL for the Google Solar API
url = "https://solar.googleapis.com/v1/buildingInsights:findClosest"

# Get and extract required attributes from API response
def get_building_insights(latitude, longitude, quality="HIGH"):
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
                return response, None

        # Extract relevant information for summary
        building_insight = {
            "center_latitude": response['center']['latitude'],
            "center_longitude": response['center']['longitude'],
            "NumPanels": response['solarPotential']['solarPanelConfigs'][-1]['panelsCount'],
            "YearlyEnergy": response['solarPotential']['solarPanelConfigs'][-1]['yearlyEnergyDcKwh'],
            "SolarArea": response['solarPotential']['maxArrayAreaMeters2']
        }

        return response, building_insight

    except Exception as e:
        print(f"An unexpected error occurred for ({latitude}, {longitude}): {e}")
        return None, None


# Process the CSV and extract building insights
def process():
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
    df["NumPanels"] = None
    df["YearlyEnergy"] = None
    df["SolarArea"] = None

    # Create tqdm progress bar
    for index, row in tqdm(df.iterrows(), total=len(df), desc="Processing rows"):
        # Get building insights
        response, building_insight = get_building_insights(row[LATITUDE], row[LONGTIDUE])

        # Save the response in a JSON file if required
        if SAVE_ORIGIN_RESPONSE:
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
            df.at[index, "NumPanels"] = building_insight["NumPanels"]
            df.at[index, "YearlyEnergy"] = building_insight["YearlyEnergy"]
            df.at[index, "SolarArea"] = building_insight["SolarArea"]

    # Extract only relevant insights for saving to output JSON, ignoring rows with no insights
    subset_column = ["center_latitude", "center_longitude", "NumPanels", "YearlyEnergy", "SolarArea"]
    insights = df.dropna(subset=subset_column)
    insights_list = insights[subset_column].to_dict(orient="records")

    # Save the extracted building insights to a JSON file
    with open(WRITE_RESULT_JSON, "w") as json_file:
        json.dump(insights_list, json_file, indent=4)
    
    # Apply filters
    # Check latitude and longitude difference thresholds
    df["DataVerificationFlag"] = (
        (df["center_latitude"].notnull()) &
        (df["center_longitude"].notnull()) &
        (
            (abs(df[LATITUDE] - df["center_latitude"]) > LAT_LNG_THRESHOLD) |
            (abs(df[LONGTIDUE] - df["center_longitude"]) > LAT_LNG_THRESHOLD)
        )
    ).astype(int)

    # Filter out rows with no panels
    df = df[df["NumPanels"].notnull() & (df["NumPanels"] > 0)]

    # Flag extreme small and large panel values
    df["OutputVerificationFlag"] = (
        (df["NumPanels"] < MIN_PANELS) | (df["NumPanels"] > MAX_PANELS)
    ).astype(int)

    # Count the number of rows and abnormal flags
    total_rows = len(df)
    data_verification_flag_count = df["DataVerificationFlag"].sum()
    output_verification_flag_count = df["OutputVerificationFlag"].sum()

    # Print the counts
    print(f"Total number of rows after filtering: {total_rows}")
    print(f"Number of rows with DataVerificationFlag set to 1: {data_verification_flag_count}")
    print(f"Number of rows with OutputVerificationFlag set to 1: {output_verification_flag_count}")

    # Select different columns to 
    deliverable_1_columns = [STORE_NAME, ADDRESS, LATITUDE, LONGTIDUE, "center_latitude", "center_longitude", "DataVerificationFlag"]
    deliveravle_2_columns = [STORE_NAME, ADDRESS, LATITUDE, LONGTIDUE, "NumPanels", "YearlyEnergy", "SolarArea", "OutputVerificationFlag"]
    deliverable_1_df = df[deliverable_1_columns]
    deliverable_2_df = df[deliveravle_2_columns]

    # Save the updated DataFrame to new CSV files
    deliverable_1_df.to_csv(WRITE_RESULT_CSV_DATA_VERIF, index=False)
    deliverable_2_df.to_csv(WRITE_RESULT_CSV_OUTPUT_VERIF, index=False)

    print(f"Processing completed! Results saved to {WRITE_RESULT_JSON}, {WRITE_RESULT_CSV_DATA_VERIF} and {WRITE_RESULT_CSV_OUTPUT_VERIF}")


if __name__ == "__main__":
    # Process the CSV file and extract building insights
    process()
