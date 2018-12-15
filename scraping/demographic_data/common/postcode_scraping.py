import json
import sys
from scraping.demographic_data.common.zip_scrapers.zip_finder import ZipScraper
from scraping.demographic_data.common.zip_scrapers.zip_census import CensusScraper
from scraping.demographic_data.common.zip_scrapers.zip_square_miles import ZIPMilesScraper
from scraping.demographic_data.common.zip_scrapers.zip_crime_rate import ZIPCrimeScraper
from scraping.common.parallelize import Parallelizer

# Find zip codes
def find_zips(city_name):
    print ("Looking for zips...")
    google_zips = ZipScraper(city_name)

    with open("../data/postcode_lists/" + city_name + ".json", "w") as write_file:
        json.dump(google_zips.scrape_zips(), write_file)
    google_zips.scraper.finish()
    print ("Saved zips.")


# Load postcodes
def load_zips(city_name):
    print("Loading zips...")
    with open("../data/postcode_lists/" + city_name + ".json", "r") as read_file:
        postcodes = json.load(read_file)
    print("Loaded zips.")
    return list(set(postcodes))


def first_part(postcode_list):
    census_scraper = CensusScraper()
    postcode_info = census_scraper.show_all_tab(postcode_list)
    with open("../data/temp/1-" + city_name + ".json", "w") as write_file:
        json.dump(postcode_info, write_file)
    census_scraper.scraper.finish()
    return postcode_info


def second_part(city_name, postcode_info):
    while True:
        try:
            census_scraper = CensusScraper()
            with open("../data/temp/2-" + city_name + ".json", "w") as write_file:
                json.dump(census_scraper.income_tab(postcode_info), write_file)
            census_scraper.scraper.finish()
            break
        except Exception as e:
            print("Crashed second part - retrying")



def third_part(city_name, postcode_info):
    while True:
        try:
            census_scraper = CensusScraper()
            with open("../data/temp/3-" + city_name + ".json", "w") as write_file:
                json.dump(census_scraper.housing_tab(postcode_info), write_file)
            census_scraper.scraper.finish()
            break
        except Exception as e:
            print("Crashed third part - retrying")

def fourth_part(city_name, postcode_info):
    while True:
        try:
            crime_scraper = ZIPCrimeScraper("california/los_angeles")
            crime_rate_dict = crime_scraper.get_zips_crime(list(postcode_info.keys()))

            for postcode in crime_rate_dict.keys():
                postcode_info[str(postcode)]["violent_crime_rate"] = float(crime_rate_dict[postcode])

            with open("../data/temp/4-" + city_name + ".json", "w") as write_file:
                json.dump(postcode_info, write_file)
            break
        except Exception as e:
            print("Crashed fourth part - retrying")


def fifth_part(city_name, postcode_info):
    while True:
        try:
            census_scraper = CensusScraper()
            with open("../data/temp/5-" + city_name + ".json", "w") as write_file:
                json.dump(census_scraper.housing_tab2(postcode_info), write_file)
            census_scraper.scraper.finish()
            break
        except Exception as e:
            print("Crashed fifth part - retrying")

def sixth_part(city_name, postcode_info):
    zip_scraper = ZIPMilesScraper()
    zip_land_dict = zip_scraper.get_zips_landarea(list(postcode_info.keys()))
    for postcode in zip_land_dict.keys():
        postcode_info[str(postcode)]["population"] = (float(postcode_info[str(postcode)]["population"]) / float(
            zip_land_dict[postcode])) / 1000

    with open("../data/postcode_json/" + city_name + ".json", "w") as write_file:
        json.dump(postcode_info, write_file)
    zip_scraper.scraper.finish()

if __name__ == "__main__":

    #Get city name to get postcode data on
    city_name = sys.argv[1]

    '''
    #Find the zips
    find_zips(city_name)

    #Load the zips
    postcode_info = first_part(load_zips(city_name))

    second_part(city_name, postcode_info)
    '''
    with open("../data/temp/4-" + city_name + ".json", "r") as read_file:
        postcode_info = json.load(read_file)
    fifth_part(city_name, postcode_info)
    '''
    #Prepare function dictionary to pass to our parallelizer
    funcs = [second_part, third_part, fourth_part, fifth_part]
    func_dict = {func.__name__: {"func": func,
                                 "args": [city_name, postcode_info]
                                 } for func in funcs}
    
    paral = Parallelizer(func_dict)

    paral.run_concurrent(list(func_dict.keys()), 2)
    '''
