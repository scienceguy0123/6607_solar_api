import pandas as pd
import requests
import json
import os
import time
from tqdm import tqdm

try:
    from config import GOOGLE_API_KEY, INPUT_FILE, DELIVERABLE_1, DELIVERABLE_2, RESPONSE_JSON_DIR, \
        LAT_LNG_THRESHOLD, MIN_PANELS, MAX_PANELS
except ImportError:
    print("Error: Can't find config.py file! Please ensure the config.py file exists and contains the necessary "
          "configuration information.")
    exit(1)


# Google Maps geocoding
def get_latitude_longitude(input_file):
    """
    Get latitude and longitude for each address using Google Maps API.

    Parameters:
    input_file (str): Path to the input CSV file.

    Returns:
    pd.DataFrame: Updated DataFrame with latitude and longitude columns.
    """
    geocode_url = f"https://maps.googleapis.com/maps/api/geocode/json"
    df = pd.read_csv(input_file)

    if 'Address' not in df.columns or 'Store_Name' not in df.columns:
        raise ValueError("The input file does not contain the 'Address' or 'Store_Name' column.")

    df['lat'] = None
    df['lgt'] = None

    successful_count = 0  # Counter for successful geocoding

    for index, row in tqdm(df.iterrows(), total=len(df), desc="Geocoding addresses"):
        # Geocode the address (first step to get lat/lng)
        geocode_params = {
            "address": row["Address"],
            "key": GOOGLE_API_KEY
        }
        try:
            geocode_response = requests.get(geocode_url, params=geocode_params).json()

            if "results" in geocode_response and len(geocode_response["results"]) > 0:
                location = geocode_response["results"][0]["geometry"]["location"]
                df.at[index, 'lat'] = location['lat']
                df.at[index, 'lgt'] = location['lng']
                successful_count += 1  # Increment successful geocoding count
            else:
                print(f"Warning: Could not find latitude and longitude for address: {row['Address']}")
                continue
        except Exception as e:
            print(f"Unexpected error for ({row['Address']}): {e}")
            continue

    # Output the number of successful geo-codings
    print(f"Total addresses processed: {len(df)}")
    print(f"Successfully geocoded addresses: {successful_count}")
    print(f"Addresses without geocoding: {len(df) - successful_count}")

    return df


# Get building insights
def get_building_insights(df):
    """
    Get building insights from the Google Solar API.

    Parameters:
    df (pd.DataFrame): Input DataFrame with latitude and longitude.

    Returns:
    pd.DataFrame: Updated DataFrame with building insights columns.
    """
    url = "https://solar.googleapis.com/v1/buildingInsights:findClosest"
    df["center_latitude"] = None
    df["center_longitude"] = None
    df["NumPanels"] = None
    df["YearlyEnergy"] = None
    df["SolarArea"] = None

    os.makedirs(RESPONSE_JSON_DIR, exist_ok=True)

    high_quality_count = 0  # Count for high-quality insights
    medium_quality_count = 0  # Count for medium-quality insights
    not_found_count = 0  # Count for not-found results

    for index, row in tqdm(df.iterrows(), total=len(df), desc="Getting building insights"):
        params = {
            "location.latitude": row["lat"],
            "location.longitude": row["lgt"],
            "requiredQuality": "HIGH",
            "key": GOOGLE_API_KEY
        }
        try:
            response = requests.get(url, params=params).json()

            # Check for error and fallback to medium quality
            if "error" in response:
                if response["error"]["status"] == "NOT_FOUND":
                    params["requiredQuality"] = "MEDIUM"
                    response = requests.get(url, params=params).json()

                    if "error" in response:
                        not_found_count += 1  # Increment not-found count
                        print(f"Not found for ({row['Address']}) at medium quality.")
                        continue
                    else:
                        medium_quality_count += 1  # Increment medium-quality count
                else:
                    not_found_count += 1  # Increment not-found count
                    print(f"Error for ({row['Address']}): {response['error']['message']}")
                    continue
            else:
                high_quality_count += 1  # Increment high-quality count

            building_insight = {
                "center_latitude": response['center']['latitude'],
                "center_longitude": response['center']['longitude'],
                "NumPanels": response['solarPotential']['solarPanelConfigs'][-1]['panelsCount'],
                "YearlyEnergy": response['solarPotential']['solarPanelConfigs'][-1]['yearlyEnergyDcKwh'],
                "SolarArea": response['solarPotential']['maxArrayAreaMeters2']
            }

            # Save response JSON files in directory
            store_name = row.get("Store_Name", "unknown").replace(" ", "_").replace("/", "-")
            filename = f"{RESPONSE_JSON_DIR}/{store_name}.json"
            with open(filename, "w") as response_file:
                json.dump(response, response_file, indent=4)

            df.at[index, "center_latitude"] = building_insight["center_latitude"]
            df.at[index, "center_longitude"] = building_insight["center_longitude"]
            df.at[index, "NumPanels"] = building_insight["NumPanels"]
            df.at[index, "YearlyEnergy"] = building_insight["YearlyEnergy"]
            df.at[index, "SolarArea"] = building_insight["SolarArea"]

        except Exception as e:
            not_found_count += 1  # Increment not-found count for exceptions
            print(f"Unexpected error for ({row['Address']}): {e}")
            continue

    # Output the counts
    print(f"Total addresses processed: {len(df)}")
    print(f"High-quality insights found: {high_quality_count}")
    print(f"Medium-quality insights found: {medium_quality_count}")
    print(f"Not found: {not_found_count}")

    return df


# Apply filters and save results
def apply_filters_and_save(df):
    """
    Apply filters, save deliverable files, and generate a JSON report.

    Parameters:
    df (pd.DataFrame): DataFrame with geocoded addresses and building insights.
    """
    # Apply data verification flag
    df["DataVerificationFlag"] = (
        (df["center_latitude"].notnull()) &
        (df["center_longitude"].notnull()) &
        (
            (abs(df["lat"] - df["center_latitude"]) > LAT_LNG_THRESHOLD) |
            (abs(df["lgt"] - df["center_longitude"]) > LAT_LNG_THRESHOLD)
        )
    ).astype(int)

    # Apply output verification flag
    df["OutputVerificationFlag"] = (
        (df["NumPanels"] < MIN_PANELS) | (df["NumPanels"] > MAX_PANELS)
    ).astype(int)

    # Filter rows with valid NumPanels
    df = df[df["NumPanels"].notnull() & (df["NumPanels"] > 0)]

    # Count flags
    data_verification_count = df["DataVerificationFlag"].sum()
    output_verification_count = df["OutputVerificationFlag"].sum()

    # Define deliverable columns
    deliverable_1_columns = ["Store_Name", "Address", "lat", "lgt", "center_latitude", "center_longitude",
                             "DataVerificationFlag"]
    deliverable_2_columns = ["Store_Name", "Address", "lat", "lgt", "NumPanels", "YearlyEnergy", "SolarArea",
                             "OutputVerificationFlag"]

    # Create deliverables
    deliverable_1_df = df[deliverable_1_columns]
    deliverable_2_df = df[deliverable_2_columns]

    # Save to CSV
    deliverable_1_df.to_csv(DELIVERABLE_1, index=False)
    deliverable_2_df.to_csv(DELIVERABLE_2, index=False)

    # Output results
    print(f"Number of rows without none-value: {len(df)}")
    print(f"Number of rows with DataVerificationFlag set to 1: {data_verification_count}")
    print(f"Number of rows with OutputVerificationFlag set to 1: {output_verification_count}")
    print(f"Processing completed! Results saved to {DELIVERABLE_1} and {DELIVERABLE_2}")
    

# Main execution
if __name__ == "__main__":
    # Record the start time
    start_time = time.time()

    geocoded_df = get_latitude_longitude(INPUT_FILE)
    insights_df = get_building_insights(geocoded_df)
    apply_filters_and_save(insights_df)

    # Record the end time
    end_time = time.time()

    # Calculate and print the total runtime
    total_time = end_time - start_time
    print(f"Total runtime: {total_time:.2f} seconds")
