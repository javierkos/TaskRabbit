from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
import json
import time
import pandas as pd
from scraping.demographic_data.common.zip_scrapers.zip_square_miles import ZIPMilesScraper
from scraping.demographic_data.common.zip_scrapers.zip_crime_rate import ZIPCrimeScraper

# Click on Element
def safe_element_click(element, driver):
    webdriver.ActionChains(driver).move_to_element(element).click(element).perform()

#Set-up
chrome_options = Options()
driver = webdriver.Chrome(executable_path=r'/usr/bin/chromedriver', chrome_options=chrome_options)
wait = WebDriverWait(driver, 10)

#Access census site
driver.get("https://factfinder.census.gov/faces/nav/jsf/pages/community_facts.xhtml")
time.sleep(3)

#Load postcodes
with open("data/san_francisco_postcodes.json", "r") as read_file:
    postcodes = json.load(read_file)
postcode_list = list(set([int(postcodes[location]) for location in postcodes.keys()]))

'''
#First part, some common data found in "show all" tab

#Search bar and button for postcode
search = driver.find_element_by_css_selector("#cfsearchtextbox")
search_button = driver.find_element_by_css_selector(".aff-btn")
time.sleep(3)

#Click on show all measures
safe_element_click(driver.find_element_by_xpath("//a[contains(text(), 'Show')]"), driver)
time.sleep(3)

postcode_info = {}
for postcode in postcode_lists:
    print (postcode)
    #Send postcode and click go
    search.clear()
    search.send_keys(str(postcode))
    search_button.click()
    time.sleep(8)

    #Get total population
    population = int(driver.find_elements_by_xpath("//tr/td[contains(text(), '2016 ACS 5-Year Population Estimate')]/following-sibling::td")[0].text.replace(",", ""))
    median_age = driver.find_elements_by_xpath("//tr/td[contains(text(), 'Median Age')]/following-sibling::td")[0].text
    per_below_poverty = driver.find_elements_by_xpath("//tr/td[contains(text(), 'Individuals below pov')]/following-sibling::td")[0].text.replace("%", "")
    per_highschool = driver.find_elements_by_xpath("//tr/td[contains(text(), 'Educational Attainment: Percent high')]/following-sibling::td")[0].text.replace("%", "")
    per_white = int(driver.find_elements_by_xpath("//tr/td[contains(text(), 'White alone')]/following-sibling::td")[0].text.replace(",", ""))/population * 100
    median_household_income = driver.find_elements_by_xpath("//tr/td[contains(text(), 'Median Household Income')]/following-sibling::td")[0].text.replace(",", "")
    per_foreign_born = int(driver.find_elements_by_xpath("//tr/td[contains(text(), 'Foreign Born')]/following-sibling::td")[0].text.replace(",", ""))/population * 100

    #Get data
    postcode_info[postcode] = {}
    postcode_info[postcode]["population"] = population
    postcode_info[postcode]["median_age"] = median_age
    postcode_info[postcode]["per_below_poverty"] = per_below_poverty
    postcode_info[postcode]["per_highschool"] = per_highschool
    postcode_info[postcode]["per_white"] = str(round(per_white, 2))
    postcode_info[postcode]["median_household_income"] = median_household_income
    postcode_info[postcode]["per_foreign_born"] = str(round(per_foreign_born, 2))

time.sleep(3)

#Second part, unemployment rate

# Click on Income tab
safe_element_click(driver.find_element_by_xpath("//a[contains(text(), 'Income')]"), driver)
time.sleep(3)

for postcode in postcode_lists:
    # Search bar and button for postcode
    search = driver.find_element_by_css_selector("#cfsearchtextbox")
    search_button = driver.find_element_by_css_selector(".aff-btn")
    time.sleep(3)

    # Send postcode and click go
    search.clear()
    search.send_keys(str(postcode))
    search_button.click()
    time.sleep(5)

    # Open economic characteristic table
    driver.find_element_by_xpath(
        "//h3[contains(text(), '2016')]/following-sibling::ul//a[contains(text(), 'Selected Economic Characteristics')]").click()
    time.sleep(3)

    # Get unemployment rate
    unemployment_rate = driver.find_elements_by_xpath("//th[contains(text(), 'Unemployment Rate')]/following-sibling::td")[2].text.replace(
        "%", "")
    postcode_info[str(postcode)]["unemployment_rate"] = unemployment_rate
    print(postcode_info[str(postcode)]["unemployment_rate"])
    driver.back()

time.sleep(3)

#Third part, homeownership rate

# Click on Housing tab
safe_element_click(driver.find_element_by_xpath("//a[contains(text(), 'Housing')]"), driver)
time.sleep(3)

for postcode in postcode_lists:
    print (postcode)
    # Search bar and button for postcode
    search = driver.find_element_by_css_selector("#cfsearchtextbox")
    search_button = driver.find_element_by_css_selector(".aff-btn")
    time.sleep(3)

    # Send postcode and click go
    search.clear()
    search.send_keys(str(postcode))
    search_button.click()
    time.sleep(5)

    # Open housing characteristic table
    driver.find_element_by_xpath(
        "//h3[contains(text(), '2016')]/following-sibling::ul//a[contains(text(), 'Selected Housing Characteristics')]").click()
    time.sleep(3)

    # Get ownership rate
    ownership_rate = driver.find_elements_by_xpath("//th[contains(text(), 'Owner-occupied')]/following-sibling::td")[2].text.replace(
        "%", "")
    postcode_info[str(postcode)]["ownership_rate"] = ownership_rate
    print (postcode_info[str(postcode)]["ownership_rate"])
    driver.back()


#4th part, population density

zip_scraper = ZIPMilesScraper()
zip_land_dict = zip_scraper.get_zips_landarea(postcode_lists)
for postcode in zip_land_dict.keys():
    postcode_info[str(postcode)]["population"] = (float(postcode_info[str(postcode)]["population"])/float(zip_land_dict[postcode]))/1000



time.sleep(3)
#Load postcodes
with open("data/temp_data.json", "r") as read_file:
    postcode_info = json.load(read_file)

# Click on Housing tab
safe_element_click(driver.find_element_by_xpath("//a[contains(text(), 'Housing')]"), driver)
time.sleep(3)

for postcode in postcode_lists:
    print (postcode)
    # Search bar and button for postcode
    search = driver.find_element_by_css_selector("#cfsearchtextbox")
    search_button = driver.find_element_by_css_selector(".aff-btn")
    time.sleep(3)

    # Send postcode and click go
    search.clear()
    search.send_keys(str(postcode))
    search_button.click()
    time.sleep(5)

    # Open housing characteristic table
    driver.find_element_by_xpath(
        "//h3[contains(text(), '2016')]/following-sibling::ul//a[contains(text(), 'Financial Characteristics')]").click()
    time.sleep(3)

    # Get ownership rate
    median_rent = driver.find_elements_by_xpath("//th[contains(text(), 'Median (dollars)')]/following-sibling::td")[4].text.replace(
        ",", "")
    postcode_info[str(postcode)]["median_rent"] = median_rent
    print (postcode_info[str(postcode)]["median_rent"])
    driver.back()

with open("data/temp_data.json", "w") as write_file:
    json.dump(postcode_info, write_file)
    
'''
time.sleep(3)
#Load postcodes
with open("data/temp_data.json", "r") as read_file:
    postcode_info = json.load(read_file)

crime_scraper = ZIPCrimeScraper("california/san_francisco")
crime_rate_dict = crime_scraper.get_zips_crime(postcode_list)

for postcode in postcode_list:
    postcode_info[str(postcode)]["violent_crime_rate"] = float(crime_rate_dict[postcode])

with open("data/temp_data.json", "w") as write_file:
    json.dump(postcode_info, write_file)