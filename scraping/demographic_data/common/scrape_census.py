import json
import sys
from scraping.demographic_data.common.constants import CITY_SPACE, CITY_UNDER
from scraping.demographic_data.common.zip_scrapers.zip_finder import ZipScraper
from scraping.demographic_data.common.zip_scrapers.zip_census import CensusScraper
from scraping.demographic_data.common.zip_scrapers.zip_square_miles import ZIPMilesScraper
from scraping.demographic_data.common.zip_scrapers.zip_crime_rate import ZIPCrimeScraper

census_scraper = CensusScraper()
postcode_list = []
dir = "../" + CITY_UNDER + "/"

'''
    Census scraping divided in 6 parts
'''

# Find zip codes
def find_zips():
    google_zips = ZipScraper(CITY_SPACE)

    with open(dir + "data/postcodes.json", "w") as write_file:
        json.dump(google_zips.scrape_zips(), write_file)


# Load postcodes
def load_zips():
    global postcode_list
    with open(dir + "data/postcodes.json", "r") as read_file:
        postcodes = json.load(read_file)
    postcode_list = list(set(postcodes))


def first_part():
    global postcode_list
    with open(dir + "data/temp_data.json", "w") as write_file:
        json.dump(census_scraper.show_all_tab(postcode_list), write_file)


def second_part():
    global postcode_list

    with open(dir + "data/temp_data.json", "r") as read_file:
        postcode_info = json.load(read_file)
    with open(dir + "data/temp_data_2.json", "w") as write_file:
        json.dump(census_scraper.income_tab(postcode_info), write_file)


def third_part():
    global postcode_list

    with open(dir + "data/temp_data_2.json", "r") as read_file:
        postcode_info = json.load(read_file)
    with open(dir + "data/temp_data_3.json", "w") as write_file:
        json.dump(census_scraper.housing_tab(postcode_info), write_file)


def fourth_part():
    global postcode_list

    with open(dir + "data/temp_data_3.json", "r") as read_file:
        postcode_info = json.load(read_file)

    zip_scraper = ZIPMilesScraper()
    zip_land_dict = zip_scraper.get_zips_landarea(list(postcode_info.keys()))
    for postcode in zip_land_dict.keys():
        postcode_info[str(postcode)]["population"] = (float(postcode_info[str(postcode)]["population"]) / float(
            zip_land_dict[postcode])) / 1000

    with open(dir + "data/temp_data_4.json", "w") as write_file:
        json.dump(postcode_info, write_file)


def fifth_parth():
    with open(dir + "data/temp_data_4.json", "r") as read_file:
        postcode_info = json.load(read_file)

    crime_scraper = ZIPCrimeScraper(CITY_SPACE)
    crime_rate_dict = crime_scraper.get_zips_crime(list(postcode_info.keys()))

    for postcode in crime_rate_dict.keys():
        postcode_info[str(postcode)]["violent_crime_rate"] = float(crime_rate_dict[postcode])

    with open(dir + "data/temp_data_5.json", "w") as write_file:
        json.dump(postcode_info, write_file)


def sixth_part():
    with open(dir + "data/temp_data_5.json", "r") as read_file:
        postcode_info = json.load(read_file)

    with open(dir + "data/data.json", "w") as write_file:
        json.dump(census_scraper.housing_tab2(postcode_info), write_file)


if __name__ == "__main__":
    funcs = {
        "find_zips": find_zips,
        "load_zips": load_zips,
        "first_part": first_part,
        "second_part": second_part,
        "third_part": third_part,
        "fourth_part": fourth_part,
        "fifth_part": fifth_parth,
        "sixth_part": sixth_part
    }

    for f in sys.argv[1:]:
        funcs[f]()
