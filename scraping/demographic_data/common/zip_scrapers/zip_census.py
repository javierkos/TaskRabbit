import time
from scraping.page_scraper import PageScraper
from selenium import webdriver

pages = [
    # Main page where services are listed
    {
        "name": "census_finder",

        "search_bar": "#cfsearchtextbox",
        "search_button": ".aff-btn"

    },
]

class CensusScraper:

    def __init__(self):
        self.scraper = PageScraper(pages, "https://factfinder.census.gov/faces/nav/jsf/pages/community_facts.xhtml")
        self.scraper.change_current_page("census_finder")
        time.sleep(3)

    # Click on Element
    def safe_element_click(self, element):
        webdriver.ActionChains(self.scraper.driver).move_to_element(element).click(element).perform()
        
    # First part, some common data found in "show all" tab
    def show_all_tab(self, postcode_list):

        # Search bar and button for postcode
        search = self.scraper.find_elements(["search_bar"])[0]
        search_button = self.scraper.find_elements(["search_button"])[0]
        time.sleep(3)

        # Click on show all measures
        self.safe_element_click(self.scraper.driver.find_element_by_xpath("//a[contains(text(), 'Show')]"))
        time.sleep(3)

        postcode_info = {}
        for postcode in postcode_list:
            # Send postcode and click go
            search.clear()
            search.send_keys(str(postcode))
            self.safe_element_click(search_button)
            time.sleep(8)

            # Get total population
            population = int(self.scraper.driver.find_elements_by_xpath(
                "//tr/td[contains(text(), '2017 ACS 5-Year Population Estimate')]/following-sibling::td")[
                                 0].text.replace(",", ""))
            if population == 0:
                print("Reject: " + postcode)
                continue
            median_age = self.scraper.driver.find_elements_by_xpath("//tr/td[contains(text(), 'Median Age')]/following-sibling::td")[
                0].text
            per_below_poverty = self.scraper.driver.find_elements_by_xpath("//tr/td[contains(text(), 'Individuals below pov')]/following-sibling::td")[
                0].text.replace("%", "")
            per_highschool = self.scraper.driver.find_elements_by_xpath(
                "//tr/td[contains(text(), 'Educational Attainment: Percent high')]/following-sibling::td")[
                0].text.replace("%", "")
            per_white = int(self.scraper.driver.find_elements_by_xpath("//tr/td[contains(text(), 'White alone')]/following-sibling::td")[
                    0].text.replace(",", "")) / population * 100
            median_household_income = self.scraper.driver.find_elements_by_xpath("//tr/td[contains(text(), 'Median Household Income')]/following-sibling::td")[
                0].text.replace(",", "")
            per_foreign_born = int(self.scraper.driver.find_elements_by_xpath("//tr/td[contains(text(), 'Foreign Born')]/following-sibling::td")[
                    0].text.replace(",", "")) / population * 100

            # Get data
            postcode_info[postcode] = {}
            postcode_info[postcode]["population"] = population
            postcode_info[postcode]["median_age"] = median_age
            postcode_info[postcode]["per_below_poverty"] = per_below_poverty
            postcode_info[postcode]["per_highschool"] = per_highschool
            postcode_info[postcode]["per_white"] = str(round(per_white, 2))
            postcode_info[postcode]["median_household_income"] = median_household_income
            postcode_info[postcode]["per_foreign_born"] = str(round(per_foreign_born, 2))

        time.sleep(3)
        return postcode_info

    # Second part, unemployment rate
    def income_tab(self, postcode_list):

        # Click on Income tab
        self.safe_element_click(self.scraper.driver.find_element_by_xpath("//a[contains(text(), 'Income')]"))
        postcode_dict = {}
        for i, postcode in enumerate(list(postcode_list)):
            time.sleep(2)
            # Search bar and button for postcode
            search = self.scraper.find_elements(["search_bar"])[0]
            search_button = self.scraper.find_elements(["search_button"])[0]
            time.sleep(3)

            # Send postcode and click go
            search.clear()
            search.send_keys(str(postcode))
            self.safe_element_click(search_button)
            time.sleep(5)

            # Open economic characteristic table
            self.safe_element_click(self.scraper.driver.find_element_by_xpath(
                "//h3[contains(text(), '2017')]/following-sibling::ul//a[contains(text(), 'Selected Economic Characteristics')]"))
            time.sleep(4)

            # Try to get unemployment rate
            try:
                unemployment_rate = self.scraper.driver.find_elements_by_xpath("//th[contains(text(), 'Unemployment Rate')]/following-sibling::td")[
                    2].text.replace(
                    "%", "")
            except Exception:
                del postcode_list[i]
                print("Reject:-- " + str(postcode))
                self.scraper.driver.back()
                continue

            # Check if we have a valid value
            try:
                float(unemployment_rate)
            except ValueError:
                del postcode_list[i]
                print ("Reject: " + str(postcode))
                self.scraper.driver.back()
                continue

            postcode_dict[str(postcode)] = unemployment_rate
            print(postcode_dict[str(postcode)])
            self.scraper.driver.back()

        time.sleep(3)
        return postcode_dict

    # Third part, homeownership rate
    def housing_tab(self, postcode_list):

        # Click on Housing tab
        self.safe_element_click(self.scraper.driver.find_element_by_xpath("//a[contains(text(), 'Housing')]"))
        postcode_dict = {}
        for i, postcode in enumerate(list(postcode_list)):
            time.sleep(2)
            # Search bar and button for postcode
            search = self.scraper.find_elements(["search_bar"])[0]
            search_button = self.scraper.find_elements(["search_button"])[0]
            time.sleep(3)

            # Send postcode and click go
            search.clear()
            search.send_keys(str(postcode))
            self.safe_element_click(search_button)
            time.sleep(5)

            # Open housing characteristic table
            self.safe_element_click(self.scraper.driver.find_element_by_xpath(
                "//h3[contains(text(), '2017')]/following-sibling::ul//a[contains(text(), 'Selected Housing Characteristics')]"))
            time.sleep(3)

            # Get ownership rate
            ownership_rate = self.scraper.driver.find_elements_by_xpath("//th[contains(text(), 'Owner-occupied')]/following-sibling::td")[
                2].text.replace(
                "%", "")

            # Check if we have a valid value
            try:
                float(ownership_rate)
            except ValueError:
                del postcode_list[i]
                print ("Reject: " + str(postcode))
                self.scraper.driver.back()
                continue

            postcode_dict[str(postcode)] = ownership_rate
            print(postcode_dict[str(postcode)])
            self.scraper.driver.back()

        time.sleep(3)
        return postcode_dict

    # Fourth part, median rent
    def housing_tab2(self, postcode_list):

        # Click on Housing tab
        self.safe_element_click(self.scraper.driver.find_element_by_xpath("//a[contains(text(), 'Housing')]"))
        postcode_dict = {}
        for i, postcode in enumerate(list(postcode_list)):
            time.sleep(2)
            # Search bar and button for postcode
            search = self.scraper.find_elements(["search_bar"])[0]
            search_button = self.scraper.find_elements(["search_button"])[0]
            time.sleep(3)

            # Send postcode and click go
            search.clear()
            search.send_keys(str(postcode))
            self.safe_element_click(search_button)
            time.sleep(5)

            # Open housing financial table
            self.scraper.driver.find_element_by_xpath(
                "//h3[contains(text(), '2017')]/following-sibling::ul//a[contains(text(), 'Financial Characteristics')]").click()
            time.sleep(3)

            # Get median rent
            median_rent = self.scraper.driver.find_elements_by_xpath("//th[contains(text(), 'Median (dollars)')]/following-sibling::td")[
                4].text.replace(
                ",", "")

            # Check if we have a valid value
            try:
                float(median_rent)
            except ValueError:
                del postcode_list[i]
                print ("Reject: " + str(postcode))
                self.scraper.driver.back()
                continue

            postcode_dict[str(postcode)] = median_rent
            print(postcode_dict[str(postcode)])
            self.scraper.driver.back()

        time.sleep(3)
        return postcode_dict
