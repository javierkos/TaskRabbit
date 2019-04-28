from scraping.page_scraper import PageScraper

pages = [
    # Main page where services are listed
    {
        "name": "city_data_search",

        "zips": ".zip-codes>a"
    },
]

class ZipScraper:

    def __init__(self, city_name):
        url_map = {
            "los angeles": "Los-Angeles-California",
            "san francisco": "San-Francisco-California",
            "new york": "New-York-New-York",
            "oklahoma": "Oklahoma-City-Oklahoma"
        }
        self.scraper = PageScraper(pages, "http://www.city-data.com/zipmaps/" + url_map[city_name] + ".html")
        self.scraper.change_current_page("city_data_search")

    # Returns a list
    def scrape_zips(self):
        zips = self.scraper.find_elements(["zips"])

        # Return postcode list
        return [zip.text for zip in zips]