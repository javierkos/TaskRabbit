import sqlite3
conn = sqlite3.connect('../databases/taskrabbit.db')
c = conn.cursor()

def get_locations_in_city(city_name):
    c.execute(
        "SELECT locations.name, locations.location_id FROM locations, cities WHERE cities.city_id = locations.city_id AND cities.name = '" + city_name + "';")
    temp_locations = []
    for row in c:
        temp_locations.append(row)
    return temp_locations

def get_num_taskers_per_location(locations):
    num_of_taskers = {}
    for location in locations:
        c.execute(
            "SELECT COUNT(*) FROM tasker_locations,locations WHERE tasker_locations.location_id = locations.location_id AND locations.location_id = " + str(
                location[1]) + ";")
        num_of_taskers[location[0]] = c.fetchone()[0]
    return num_of_taskers

def get_taskers_per_location(locations):
    location_taskers = {}
    for location in locations:
        c.execute(
            "SELECT tasker_id FROM tasker_locations,locations WHERE tasker_locations.location_id = locations.location_id AND locations.location_id = " + str(
                location[1]) + ";")
        location_taskers[location[0]] = [tasker[0] for tasker in c.fetchall()]
    return location_taskers