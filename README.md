# Solar Panel Data Analysis Tool

## Project Overview
This tool processes address data, retrieves geolocation information, and gathers solar panel insights using APIs. It applies filters to clean and analyze the data, producing descriptive statistics and visualizations to aid decision-making.

## Features
- Batch geocoding of addresses into latitude and longitude using the Google Maps API.
- Solar panel insights retrieval via the Google Solar API with fallback quality settings (`HIGH` → `MEDIUM`).
- Comprehensive filtering of data to remove irrelevant or invalid rows.
- Automated generation of visualizations and statistical summaries.
- Outputs clean and structured data files for further analysis.

## Updates and Enhancements

### Nov 25th, 2024
- Implemented fallback to `MEDIUM` quality when `HIGH` returns a 404 error.
- Merged geolocation and solar insights into a single CSV file.
- Introduced `config.py` for API key management and file path customization.

### Dec 1st, 2024
- Outputs the following files and directory:
  - `output.json`
  - `deliverable1.csv`
  - `deliverable2.csv`
  - `original_response/`
- Filters applied:
  - Dropped rows with no solar panels.
  - Flagged rows where differences in latitude/longitude exceed a threshold (**0.0005**).
  - Flagged rows where solar panels are outside the range (**10 to 2000**).
- Filtering results:
  - **Dropped 4 rows with no solar panels (original: 266 rows → final: 262 rows).**
  - **33 rows in `deliverable1.csv` flagged for abnormal latitude/longitude.**
  - **32 rows in `deliverable2.csv` flagged for abnormal solar panel counts.**

## Visualizations
The `demo.py` script generates the following visualizations:
- **Pie Chart of Solar Panels**
  ![Pie Chart of Solar Panels](./figure/Pie_Chart.png)

- **Histogram of Log Panel Counts**
  ![Histogram of Log Panel Counts](./figure/Histogram_KDE.png)

- **Boxplot of Solar Panel Metrics**
  ![Boxplot of Solar Panel Metrics](./figure/Boxplot.png)

- **Scatter Plot Matrix of Solar Panel Metrics**
  ![Scatter Plot Matrix of Solar Panel Metrics](./figure/Pair_Plot.png)

## Descriptive Statistics
| Statistic | NumPanels   | YearlyEnergy       | SolarArea     |
|-----------|-------------|--------------------|---------------|
| Count     | 230.000000  | 2.300000e+02      | 230.000000    |
| Mean      | 212.213043  | 1.251063e+05      | 416.691951    |
| Std       | 303.344966  | 1.836664e+05      | 595.634477    |
| Min       | 19.000000   | 8.589278e+03      | 37.307540     |
| 25%       | 81.250000   | 4.688055e+04      | 159.538830    |
| 50%       | 114.000000  | 6.727839e+04      | 223.845260    |
| 75%       | 180.750000  | 1.037875e+05      | 354.912550    |
| Max       | 1992.000000 | 1.268119e+06      | 3911.401400   |

## Requirements
- Python 3.x
- Install required packages from `requirements.txt`:
  ```bash
  pip install -r requirements.txt
  ```

## Configuration
Before running the tool, configure the `config.py` file:
- `GOOGLE_API_KEY`: Your Google Maps API key.
- `INPUT_FILE`: Path to the input CSV file containing addresses (default: `addr.csv`).
- `DELIVERABLE_1`: Path for the first filtered CSV output.
- `DELIVERABLE_2`: Path for the second filtered CSV output.
- `RESPONSE_JSON_DIR`: Directory for storing JSON responses.

## Input File Format
The input CSV file must have the following columns:
- `Address`: Contains the address to geocode.
- `Store_Name`: Identifier for the address.

## Usage
1. Prepare an input CSV file with address data.
2. Configure the `config.py` file with the appropriate API key and file paths.
3. Run the main script:
   ```bash
   python main.py
   ```
4. Run `demo.py` to generate visualizations:
   ```bash
   python demo.py
   ```

## Output
- **Files**:
  - `output.json`: Consolidated JSON of solar insights.
  - `deliverable1.csv`: Filtered data with geolocation verification.
  - `deliverable2.csv`: Filtered data with solar panel verification.
- **Directory**:
  - `original_response/`: Contains raw JSON responses from the Solar API.

## Notes
- Ensure you have a valid Google Maps API key and Google Solar API access.
- Be mindful of API usage limits and potential billing for requests.
- Customize thresholds (`LAT_LNG_THRESHOLD`, `MIN_PANELS`, `MAX_PANELS`) in `config.py` to suit your needs.
