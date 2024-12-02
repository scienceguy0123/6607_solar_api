# config.py

# Google Maps API Key
API_KEY = "Your_API_KEY"

# File paths
READ_SRC_CSV = "addr_lat_lgt.csv"  # Input CSV file
WRITE_RESULT_CSV_DATA_VERIF = "deliverable1.csv" # Output CSV file
WRITE_RESULT_CSV_OUTPUT_VERIF = "deliverable2.csv"
WRITE_RESULT_JSON = "output.json"  # Output JSON file

# Input file column
LATITUDE = "lat" 
LONGTIDUE = "lgt"
STORE_NAME = "Store_Name"
ADDRESS = "Address"

# Save original responses (True/False)
SAVE_ORIGIN_RESPONSE = True
# Directory for saving original responses
ORIGIN_RESPONSE_DIR = "original_response"

# Some filters and threshould
# Threshold for latitude/longitude difference
LAT_LNG_THRESHOLD = 0.0005
# Extreme panel values
MIN_PANELS = 10
MAX_PANELS = 2000