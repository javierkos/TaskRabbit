from scraping.page_scraper import PageScraper

pages = [
    # Main page where services are listed
    {
        "name": "zip_search_page",
        "url": "/",

        "search_bar": "#search",
        "search_button": "#page-word-search-button",

    },
]

class ZIPMilesScraper:

    def __init__(self):
        self.scraper = PageScraper(pages, "https://www.uszip.com")
        self.scraper.change_current_page("zip_search_page")

    # Returns a dictionary
    def get_zips_landarea(self, zips):
        # For each zip, search and find sq. miles
        zip_areas = {}
        for zip in zips:
            # Find search means
            self.search_bar = self.scraper.find_elements(["search_bar"])[0]
            self.search_button = self.scraper.find_elements(["search_button"])[0]

            # Search
            self.search_bar.clear()
            self.search_bar.send_keys(zip)
            self.search_button.click()
            self.scraper.driver.implicitly_wait(2)
            land_area = self.scraper.driver.find_elements_by_xpath(
                "//dt[contains(text(), 'Land area')]/following-sibling::dd")[0].text

            print (land_area)

            zip_areas[zip] = land_area
        return zip_areas