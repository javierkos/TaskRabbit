import geopandas as gpd
import pandas as pd
import matplotlib
matplotlib.use
import matplotlib.pyplot as plt
import sqlite3
import sys

''' Program to show data in a map of the city.

    Args:  
            - Argument 1: key for function to call, for reference see "main" entry at the bottom of the code
            - Argument 2: Key of the city to plot
'''
keys = {
    "los_angeles": {
        "zip_column": "Zip_Num",
        "name": "Los Angeles"
    },
    "ny": {
        "zip_column": "ZIPCODE",
        "name": "New York"
    },
    "san_francisco": {
        "zip_column": "ZIP_CODE_5",
        "name": "San Francisco",
    }
}

def show_map_vehicles_per_tasker(city_key):
    ''' Plot a map showing the number of taskers with vehicle in each postcode

        Params:
                - city_key: key of the city to plot
    '''
    conn = sqlite3.connect("../databases/taskrabbit_" + city_key + ".db")
    c = conn.cursor()
    c2 = conn.cursor()
    c.execute("SELECT locations.name, COUNT(taskers.tasker_id), locations.location_id FROM taskers, locations, tasker_locations WHERE taskers.tasker_id = tasker_locations.tasker_id AND locations.location_id = tasker_locations.location_id AND taskers.vehicles != 'None' GROUP BY locations.location_id")

    shapefile = gpd.read_file("map_boundaries/" + city_key + "/bound.shp")

    zip_key = keys[city_key]["zip_column"]
    shapefile[zip_key] = pd.to_numeric(shapefile[zip_key])
    shapefile["num_with_vehicle"] = -100
    for row in c.fetchall():
        c2.execute("SELECT COUNT(taskers.tasker_id) FROM taskers, locations AS l, tasker_locations WHERE taskers.tasker_id = tasker_locations.tasker_id AND tasker_locations.location_id = l.location_id AND l.location_id = " + str(row[2]))
        shapefile.loc[(shapefile[zip_key] == int(row[0])), ['num_with_vehicle']] = float(row[1])/float(c2.fetchone()[0])

    shapefile = shapefile[shapefile["num_with_vehicle"] != -100]

    fig, ax = plt.subplots()
    shapefile.plot(column='num_with_vehicle', cmap='OrRd', legend=True, ax=ax)
    plt.axis('off')
    fig.set_size_inches(16, 12)
    fig.savefig('ny_vehic.png')
    plt.title("Number of taskers scraped with vehicles in " + keys[city_key]["name"])
    plt.show()

def show_map_vehicles(city_key):
    ''' Plot a map showing the number of taskers with vehicle in each postcode

        Params:
                - city_key: key of the city to plot
    '''
    # Connect to database
    conn = sqlite3.connect("../databases/taskrabbit_" + city_key + ".db")
    c = conn.cursor()

    # Select postcodes with the number of taskers that have a vehicle
    c.execute("SELECT locations.name, COUNT(taskers.tasker_id) FROM taskers, locations, tasker_locations "
              "WHERE taskers.tasker_id = tasker_locations.tasker_id "
              "AND locations.location_id = tasker_locations.location_id "
              "AND taskers.vehicles != 'None' GROUP BY locations.location_id")

    # Load shape file of map for the current city
    shapefile = gpd.read_file("map_boundaries/" + city_key + "/bound.shp")

    # Load zip keys
    zip_key = keys[city_key]["zip_column"]
    shapefile[zip_key] = pd.to_numeric(shapefile[zip_key])
    shapefile["num_with_vehicle"] = -100

    # For each postcode, set the data
    for row in c.fetchall():
        shapefile.loc[(shapefile[zip_key] == int(row[0])), ['num_with_vehicle']] = float(row[1])

    shapefile = shapefile[shapefile["num_with_vehicle"] != -100]

    # Plot
    fig, ax = plt.subplots()
    shapefile.plot(column='num_with_vehicle', cmap='OrRd', legend=True, ax=ax)
    plt.axis('off')
    fig.set_size_inches(16, 12)
    plt.title("Number of taskers scraped with vehicles in " + keys[city_key]["name"])
    plt.show()

def show_map_ethnic(city_key):
    ''' Plot a map showing the number of white taskers in each postcode

        Params:
                - city_key: key of the city to plot
    '''
    # Connect to database
    conn = sqlite3.connect("../databases/taskrabbit_" + city_key + ".db")
    c = conn.cursor()
    c2 = conn.cursor()

    # Load shape file of map for the current city
    shapefile = gpd.read_file("map_boundaries/" + city_key + "/bound.shp")

    # Load zip keys
    zip_key = keys[city_key]["zip_column"]
    shapefile[zip_key] = pd.to_numeric(shapefile[zip_key])
    shapefile["num_white"] = -100

    # For each postcode, get ethnic count for white taskers
    c.execute("SELECT locations.location_id, name FROM locations")
    for row in c.fetchall():
        c2.execute("SELECT ethnicity, COUNT(*) FROM tasker_img_predictions, tasker_locations, taskers, locations WHERE tasker_locations.location_id =locations.location_id AND tasker_locations.tasker_id = taskers.tasker_id AND locations.location_id = " + str(row[0]) + " AND tasker_img_predictions.tasker_id = taskers.tasker_id AND ethnicity = 'WHITE' GROUP BY ethnicity;")
        shapefile.loc[(shapefile[zip_key] == int(row[1])), ['num_white']] = int(c2.fetchone()[1])

    shapefile = shapefile[shapefile["num_white"] != -100]

    # Plot
    fig, ax = plt.subplots()
    shapefile.plot(column='num_white', cmap='OrRd', legend=True, ax=ax)
    plt.axis('off')
    fig.set_size_inches(16, 12)
    plt.title("Number of white taskers in " + keys[city_key]["name"])
    plt.show()

def show_median_price(city_key):
    ''' Plot a map showing the median price disparity in each postcode

        Params:
                - city_key: key of the city to plot
    '''

    # Connect to database
    conn = sqlite3.connect("../databases/taskrabbit_" + city_key + ".db")
    c = conn.cursor()
    c2 = conn.cursor()

    # Load shape file of map for the current city
    shapefile = gpd.read_file("map_boundaries/" + city_key + "/bound.shp")

    # Load zip keys
    zip_key = keys[city_key]["zip_column"]
    shapefile[zip_key] = pd.to_numeric(shapefile[zip_key])
    shapefile["num_white"] = -100

    # For each postcode, get ethnic count for white taskers and divide by total
    c.execute("SELECT locations.location_id, name FROM locations")
    for row in c.fetchall():
        c2.execute("SELECT price_details.amount "
                   "FROM price_details "
                   "INNER JOIN taskers ON price_details.tasker_id = taskers.tasker_id "
                   "INNER JOIN tasker_locations ON taskers.tasker_id = tasker_locations.tasker_id "
                   "WHERE price_details.service_id = 1 AND tasker_locations.location_id = " + str(row[0]))
        total = 0
        count = 0
        for row_2 in c2.fetchall():
            total += row_2[0]
            count += 1

        # Set value in the mapping file
        shapefile.loc[(shapefile[zip_key] == int(row[1])), ['num_white']] = total/count

    shapefile = shapefile[shapefile["num_white"] != -100]

    #Plot
    fig, ax = plt.subplots()
    shapefile.plot(column='num_white', cmap='OrRd', legend=True, ax=ax)
    plt.axis('off')
    fig.set_size_inches(16, 12)
    fig.savefig('ny_disp_1.png')
    fig.set_size_inches(16, 12)
    plt.show()


def show_map_ethnic_prop(city_key):
    ''' Plot a map showing the proportion of white taskers in each postcode

        Params:
                - city_key: key of the city to plot
    '''

    # Connect to database
    conn = sqlite3.connect("../databases/taskrabbit_" + city_key + ".db")
    c = conn.cursor()
    c2 = conn.cursor()

    # Load shape file of map for the current city
    shapefile = gpd.read_file("map_boundaries/" + city_key + "/bound.shp")

    # Load zip keys
    zip_key = keys[city_key]["zip_column"]
    shapefile[zip_key] = pd.to_numeric(shapefile[zip_key])
    shapefile["num_white"] = -100

    # For each postcode, get ethnic count for white taskers and divide by total
    c.execute("SELECT locations.location_id, name FROM locations")
    for row in c.fetchall():
        c2.execute(
            "SELECT ethnicity, COUNT(*) FROM tasker_img_predictions, tasker_locations, taskers, locations "
            "WHERE tasker_locations.location_id =locations.location_id AND tasker_locations.tasker_id = taskers.tasker_id "
            "AND locations.location_id = " + str(row[0]) +
            " AND tasker_img_predictions.tasker_id = taskers.tasker_id GROUP BY ethnicity;")
        total = 0
        dict_num = {}
        for row_2 in c2.fetchall():
            total += row_2[1]
            dict_num[row_2[0]] = row_2[1]

        # Set value in the mapping file
        shapefile.loc[(shapefile[zip_key] == int(row[1])), ['num_white']] = int(dict_num["WHITE"])/total

    shapefile = shapefile[shapefile["num_white"] != -100]

    #Plot
    fig, ax = plt.subplots()
    shapefile.plot(column='num_white', cmap='OrRd', legend=True, ax=ax)
    plt.axis('off')
    fig.set_size_inches(16, 12)
    plt.title("Number of white taskers in " + keys[city_key]["name"])
    plt.show()

if __name__ == '__main__':
    funcs = {
        "taskers_with_vehicles": show_map_vehicles,
        "taskers_with_vehicles_prop": show_map_vehicles_per_tasker,
        "taskers_white": show_map_ethnic,
        "taskers_white_prop": show_map_ethnic_prop,
        "price_dispersion": show_median_price
    }

    funcs[sys.argv[1]](sys.argv[2])



