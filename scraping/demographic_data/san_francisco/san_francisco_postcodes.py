import json
import sys
from scraping.demographic_data.common.zip_scrapers.zip_finder import ZipScraper
from scraping.demographic_data.common.zip_scrapers.zip_census import CensusScraper

census_scraper = CensusScraper()
postcode_list = []

# Find zip codes
def find_zips():
    google_zips = GoogleZipScraper("san francisco")

    with open("data/postcodes.json", "w") as write_file:
        json.dump(google_zips.scrape_zips(), write_file)

# Load postcodes
def load_zips():
    global postcode_list
    with open("data/postcodes.json", "r") as read_file:
        postcodes = json.load(read_file)
    postcode_list = list(set(postcodes))

def first_part():
    global postcode_list

    postcodes = census_scraper.show_all_tab(postcode_list)

    #if postcodes == -1:

    with open("data/temp_data.json", "w") as write_file:
        json.dump(postcodes, write_file)




if __name__ == "__main__":
    funcs = {
        "find_zips": find_zips,
        "load_zips": load_zips,
        "first_part": first_part,
    }
    for f in sys.argv[1:]: funcs[f]()
