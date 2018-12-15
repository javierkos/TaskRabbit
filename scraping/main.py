import sqlite3
import sys
import constants
import os
import traceback
from scraping.database_caller import DatabaseCaller
from scraping.task_rabbit_scraper_locations import TaskRabbitScraper

def alertFail():
    os.system('say "El bot ha faileado"')
    exit(1)

def start_scraper(service, locations, dbc, start_location = None):
    print (start_location)
    print("Start scraping " + service[1])
    rabbitScrapper = TaskRabbitScraper(dbc)
    rabbitScrapper.scrapeService(service, locations, start_location)

def main(params):
    try:
        conn = sqlite3.connect('../databases/' + constants.DB_NAME)
        dbc = DatabaseCaller(conn)

        locations = dbc.getLocations(params["city"])
        services = dbc.getServices()

        started = False

        for count, service in enumerate(services):
            print ("Service " + str(count))
            if count < int(params["start_service"]):
                continue
            elif not started:
                started = True
                start_scraper(service, locations, dbc, params["start_location"])
            else:
                start_scraper(service, locations, dbc, None)
    except Exception as e:
        traceback.print_exc()
        print(e)
        print (repr(e))
        alertFail()

if __name__ == "__main__":
    if len(sys.argv[1:]) == 0:
        print ("No arguments passed - aborting...")
    else:
        # Parameters to begin scraping starting at a certain point
        params = {
            "city": sys.argv[1],
            "start_service": sys.argv[2] if len(sys.argv) > 2 else 0,
            "start_location": sys.argv[3] if len(sys.argv) > 3 else None
        }
        main(params)

'''
with Pool(3) as p:
    p.starmap(start_scraper, list(zip(services, repeat(locations))))
'''