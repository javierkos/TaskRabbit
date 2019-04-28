import requests
from bs4 import BeautifulSoup
"""
    For this scraper we can simply use beautifulsoup and requests as the site is less complex
    
    Scrapes the violent crime rate for the zip codes passed.
"""
class ZIPCrimeScraper:

    def __init__(self, location_key):
        url_map = {
            "los angeles": "california/los_angeles",
            "new york": "new_york/new_york",
            "san francisco": "california/san_francisco"
        }
        self.base_url = "https://www.bestplaces.net/crime/zip-code/" + url_map[location_key] + "/"

    # Returns a dictionary
    def get_zips_crime(self, zips):
        # For each zip, search and find sq. miles
        zip_areas = {}
        for zip in zips:
            result = requests.get(self.base_url + str(zip))

            c = result.content
            soup = BeautifulSoup(c)
            try:
                crime_rate = soup.find_all("h5")[0].text.split("violent crime is ")[1].split(".  ")[0]
            except Exception:
                print("Reject: " + str(zip))
                continue

            print (crime_rate)
            zip_areas[zip] = crime_rate
        return zip_areas