import types

class DatabaseCaller:

    def __init__(self, conn):
        self.conn = conn

    def __getattribute__(self, attr):
        method = object.__getattribute__(self, attr)
        if not method:
            raise Exception("Method %s not implemented" % attr)
        if type(method) == types.MethodType:
            self.c = self.conn.cursor()
        return method
    
    def tasker_exists(self, tasker_id):
        self.c.execute("SELECT * FROM taskers WHERE tasker_id = " + tasker_id + ";")

        if not len(self.c.fetchall()) > 0:
            return 0
        return 1

    def tasker_location_exists(self, tasker_id, location_id):
        self.c.execute("SELECT * FROM tasker_locations WHERE tasker_id = " + tasker_id + " AND location_id = " + str(location_id) + ";")

        if not len(self.c.fetchall()) > 0:
            return 0
        return 1

    def description_exists(self, service_id, tasker_id):
        self.c.execute("SELECT * FROM descriptions WHERE tasker_id = " + tasker_id + " AND service_id = " + str(service_id) + ";")

        if not len(self.c.fetchall()) > 0:
            return 0
        return 1

    def completed_exists(self, service_id, tasker_id):
        self.c.execute("SELECT * FROM completed_tasks WHERE tasker_id = " + tasker_id + " AND service_id = " + str(service_id) + ";")

        if not len(self.c.fetchall()) > 0:
            return 0
        return 1

    def price_details_exist(self, service_id, tasker_id):
        self.c.execute("SELECT * FROM price_details WHERE tasker_id = " + tasker_id + " AND service_id = " + str(service_id) + ";")

        if not len(self.c.fetchall()) > 0:
            return 0
        return 1

    def store_tasker(self, tasker):
        self.c.execute('INSERT INTO taskers(tasker_id,name,vehicles,picture) values (?,?,?,?)', tasker)
        self.conn.commit()

    def store_locations(self, locations):
        self.c.executemany('INSERT INTO locations(name,city_id) values (?,?)', locations)
        self.conn.commit()
        return self.c.lastrowid

    def store_location_data(self, location_data):
        query = 'INSERT INTO location_demographics(' \
                'location_id,' \
                'population,' \
                'density_per_mile_thousands,' \
                'median_age,' \
                'percent_highschool_plus,' \
                'homeownership_rate,' \
                'median_household_income,' \
                'foreign_born,' \
                'percent_below_poverty,' \
                'crime_rate_per_thousand_residents,' \
                'per_white,' \
                'unemployment_rate,' \
                'median_rent) values(?,?,?,?,?,?,?,?,?,?,?,?,?)'
        self.c.executemany(query, location_data)
        self.c.execute('SELECT max(location_id) FROM location_demographics')
        max_id = self.c.fetchone()[0]
        self.conn.commit()
        
        return max_id

    def store_reviews(self, reviews):
        self.c.executemany('INSERT INTO reviews(text, date, rating, tasker_id, service_title) values (?,?,?,?,?)', reviews)
        self.conn.commit()

    def store_services(self, services):
        self.c.executemany('INSERT INTO services(name,url) values (?,?)', services)
        self.conn.commit()

    def store_tasker_location(self, tasker_location):
        self.c.executemany('INSERT INTO tasker_locations(tasker_id,location_id) values (?,?)', tasker_location)
        self.conn.commit()

    def store_description(self, description):
        self.c.executemany('INSERT INTO descriptions(text,service_id,tasker_id) values (?,?,?)', description)
        self.conn.commit()

    def store_price_details(self, price_details):
        self.c.executemany('INSERT INTO price_details(amount,currency,basis,tasker_id,service_id) values (?,?,?,?,?)', price_details)
        self.conn.commit()

    def store_completed_tasks(self, completed_tasks):
        self.c.executemany('INSERT INTO completed_tasks(tasker_id,service_id,completed) values (?,?,?)', completed_tasks)
        self.conn.commit()

    # Get locations for a city
    def get_locations(self, city):
        locations = {city: []}
        self.c.execute(
            "SELECT locations.location_id,locations.name FROM locations,cities WHERE locations.city_id = cities.city_id AND cities.name = '" + city + "';")
        for row in self.c:
            locations[city].append(row)
        return locations

    # Get services
    def get_services(self):
        services = []
        self.c.execute("SELECT service_id,name,url FROM services;")
        for row in self.c:
            services.append(row)
        return services