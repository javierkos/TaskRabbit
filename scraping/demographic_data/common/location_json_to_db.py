import sqlite3
import sys
import os
import json
from scraping.database_caller import DatabaseCaller
from pathlib import Path

'''
    Takes the name of the database and the name of the city folder, inserts the data from the JSON into the DB
'''

def main(params):
    db_file = Path("../../../databases/" + params["db_name"])
    city_file = Path("../data/postcode_json/" + params["city_name"] +".json")

    #Check db file exists
    if os.path.isfile(db_file.resolve()):
        conn = sqlite3.connect(db_file.resolve())
    else:
        raise FileNotFoundError("Database file not found in the databases directory")

    #Check city folder exists
    try:
        with open(city_file.resolve(), 'r') as city_json:
            city_data = json.load(city_json)
    except FileNotFoundError:
        raise FileNotFoundError("City folder does not exist under demographic_data module")

    dbc = DatabaseCaller(conn)

    # For each location
    for location in city_data.keys():
        # Store location and get the A.I id
        location_id = dbc.store_locations([(location,1)])

        # Prepare values for the location data
        location_data = [(location_id,
            0,
            city_data[location]["population"],
            city_data[location]["median_age"],
            city_data[location]["per_highschool"],
            city_data[location]["ownership_rate"],
            city_data[location]["median_household_income"],
            city_data[location]["per_foreign_born"],
            city_data[location]["per_below_poverty"],
            city_data[location]["violent_crime_rate"],
            city_data[location]["per_white"],
            city_data[location]["unemployment_rate"],
            city_data[location]["median_rent"])]

        # Store location data
        dbc.store_location_data(location_data)

if __name__ == "__main__":
    if len(sys.argv[1:]) == 0:
        print ("No arguments passed - aborting...")
    else:
        #Database name and city folder name within scraping
        params = {
            "db_name": sys.argv[1],
            "city_name": sys.argv[2],
        }
        main(params)