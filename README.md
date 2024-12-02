## Nov 25th, 2024
*   If a request uses `HIGH` and gets a 404 not found error message, the script then tries image quality of `MEDIUM` instead.
*   Merge the `address`, `latitude`, `longtiude`, and `max responses` together into a csv file
*   Create a `config.py` and write you own api key into it. You are free to rename the file as what you like.
*   Change the files' addresses in the `config.py` to what you want to read or write.

## Dec 1st, 2024
* Ouput four files and directory: `output.json`, `deliverable1.csv`, `deliveravle2.csv` and `original_response/` 
* Filter the data before storing them into csv
    * Drop all rows with none solar panel
    * Flag up those rows where the differences between `Lat` and `center_latitude` or `Lag` and `center_longitude` excedes threshold (temporarily, **0.0005**) in deliverable1.csv
    * Flap up those rows where solar panels are smaller than the minimum threshold or larger than the maximum threshold (temporarily, minimum threshold: **10** and maximum threshold: **2000**)
* The filter results are:
    * **Drop 4 no solar panel rows from original 266 rows, i.e. 262 raws in deliveravle1.csv and deliverable2.csv**
    * **33 rows in deliverable1.csv has abnormal latitude and longitude**
    * **32 rows in deliveravle2.csv has abnoraml solar panels**
