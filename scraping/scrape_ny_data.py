from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import sqlite3

conn = sqlite3.connect('../databases/taskrabbit_ny.db')
c = conn.cursor()

chrome_options = Options()

with open("../newyork_neighbourhoods.txt") as f:
    content = f.readlines()

driver = webdriver.Chrome(executable_path=r'/usr/bin/chromedriver', chrome_options=chrome_options)
wait = WebDriverWait(driver, 10)
ids = [n for n in range(154,213)]
i = 0
for line in content:
    line = line.lower().replace("/", "-").replace(" ", "-")
    driver.get("http://furmancenter.org/neighborhoods/view/" + line)

    '''
    median_household_income = driver.find_element_by_xpath(".//div[contains(@class,'neighborhood-content')]/p").text
    median_household_income = median_household_income.split("household income in 2016 was $")[1].split(", a")[0].replace(",", "")

    driver.find_element_by_xpath(".//h3[contains(text(),'Demo')]").click()
    driver.implicitly_wait(1)

    #Demographics section
    population = driver.find_element_by_xpath(".//td[contains(text(), 'Population') and contains(@class, 'indicator-col')]/following-sibling::td[4]").text.replace(",","")
    foreign_born = driver.find_element_by_xpath(".//td[contains(text(), 'Foreign-born') and contains(@class, 'indicator-col')]/following-sibling::td[4]").text.replace("%", "")
    percent_highschool_over_25 = driver.find_element_by_xpath(".//td[contains(text(), 'high school diplo') and contains(@class, 'indicator-col')]/following-sibling::td[4]").text.replace("%", "")
    poverty_rate = driver.find_element_by_xpath(".//td[contains(text(), 'Poverty rate') and contains(@class, 'indicator-col')]/following-sibling::td[4]").text.replace("%", "")
    

    #Housing section
    driver.find_element_by_xpath(".//h3[contains(text(),'Housing Market and')]").click()
    driver.implicitly_wait(2)
    housing_units = driver.find_element_by_xpath(".//td[contains(text(), 'Homeownership') and contains(@class, 'indicator-col')]/following-sibling::td[4]").text.replace("%", "")
    print (housing_units)
    
    #Land
    driver.find_element_by_xpath(".//h3[contains(text(),'Land')]").click()
    driver.implicitly_wait(1)
    pop_density = driver.find_element_by_xpath(".//td[contains(text(), 'density') and contains(@class, 'indicator-col')]/following-sibling::td[4]").text


    #Crime
    driver.find_element_by_xpath(".//h3[contains(text(),'Neighb')]").click()
    driver.implicitly_wait(1)
    crime_rate = driver.find_element_by_xpath(".//td[contains(text(), 'crime rate (') and contains(@class, 'indicator-col')]/following-sibling::td[4]").text

    print (pop_density)

    postcode = line
    
    query = "INSERT INTO location_demographics VALUES('"\
            + str(ids[i]) + "','"\
            + population + "','"\
            + pop_density + "','"\
            + str(0) + "','"\
            + percent_highschool_over_25 + "','"\
            + housing_units + "','"\
            + median_household_income + "','"\
            + str(foreign_born) + "','"\
            + str(poverty_rate) + "','"\
            + str(crime_rate) + "')"
            
    '''

    #Housing section
    '''
    driver.find_element_by_xpath(".//h3[contains(text(),'Demo')]").click()
    driver.implicitly_wait(2)
    unemployment_rate = driver.find_element_by_xpath(".//td[contains(text(), 'Unemployment rate') and contains(@class, 'indicator-col')]/following-sibling::td[4]").text.replace("%", "")
    print (unemployment_rate)

    percent_white = driver.find_element_by_xpath(".//td[contains(text(), 'Percent white') and contains(@class, 'indicator-col')]/following-sibling::td[4]").text.replace("%", "")
    print (percent_white)
    '''
    driver.find_element_by_xpath(".//h3[contains(text(),'Rent')]").click()
    median_rent = driver.find_element_by_xpath(".//td[contains(text(), 'Median rent, all') and contains(@class, 'indicator-col')]/following-sibling::td[4]").text.replace("$", "").replace(",","")
    print (median_rent)
    query = "UPDATE location_demographics SET median_rent = " + median_rent + " WHERE location_id=" + str(ids[i]) +";"
    print (query)
    c.execute(query)
    conn.commit()
    i += 1

c.close()