import time
from selenium.common.exceptions import WebDriverException
from scraping.task_rabbit.task_rabbit_extractor import ReviewExtractor
from scraping.task_rabbit.page_data import pages
from scraping.page_scraper import PageScraper

'''
	Scrapes data from the task rabbit site using the page_scraper class
'''

class TaskRabbitScraper:
    location = None

    def __init__(self, dbc):

        self.dbc = dbc
        self.reviewExtractor = ReviewExtractor()

        # Start scraper
        self.scraper = PageScraper(pages, "https://www.taskrabbit.com/m/all-services")
        self.scraper.change_current_page("services_page")
        try:
            self.scraper.click_on_element(["cookie_dismiss_button"])
        except Exception as e:
            print ("No cookie message, continue...")

        # Form filling function switcher
        self.formFunctions = {
            "TASK INTEREST": self.fill_interest_form,
            "YOUR TASK LOCATION": self.fill_location_form,
            "START ADDRESS": self.fill_location_form,
            "END ADDRESS (OPTIONAL)": self.fill_location_form,
            "TASK OPTIONS": self.fill_task_options_form,
            "TELL US THE DETAILS OF YOUR TASK": self.fill_details_form,
            "YOUR ITEMS": self.fill_items_form
        }

    def iterate_days(self):
        days = self.scraper.find_elements(["days"])

        #If view type is the day scroller
        if not days == None:
            day_scroller = self.scraper.find_elements(["days_scroller"])
            i = 0
            for day in days:
                print (day.text)
                try:
                    self.scraper.click_on_existing_element(day)
                except WebDriverException:
                    self.scraper.click_on_existing_element(day_scroller[0])
                    self.scraper.click_on_existing_element(day)

                self.get_taskers()
                i += 1
        #If view type is the day selector
        else:
            choose_day_buton = self.scraper.find_elements(["choose_day_button"])
            if choose_day_buton:
                choose_day_buton = self.scraper.find_elements(["choose_day_button"])[0]
            else:
                return -1
            self.scraper.click_on_existing_element(choose_day_buton)
            day_buttons = self.scraper.find_elements(["calendar_days_available"])
            self.scraper.click_on_existing_element(day_buttons[1])
            self.scraper.click_on_existing_element(day_buttons[-1])
            apply_changes = self.scraper.find_elements(["apply_calendar_choice"])[0]
            self.scraper.safe_element_click(apply_changes)

            self.get_taskers()


    def get_taskers(self):

        time.sleep(2)
        tasker_divs = self.scraper.find_elements(["tasker_results"])

        #If no tasker results
        if tasker_divs == None:
            return

        #For every tasker
        i = 0
        total = len (tasker_divs)
        for tasker_div in tasker_divs:

            try:
                task_completion_info = self.scraper.find_nested_elements(tasker_div, ["tasker_info", "completed_tasks"])[
                0].text
            except Exception:
                continue
                print ("STALE ELEMENT EXCEPTION")

            tasker_id = self.scraper.find_attribute_of_nested_elements("data-user-id", tasker_div)
            # If tasker doesnt exist, scrape and store reviews.
            if not self.dbc.tasker_exists(tasker_id):
                #Vehicles
                vehicles = self.scraper.find_nested_elements(tasker_div, ["tasker_info", "vehicles"])
                if vehicles:
                    vehicle_text = vehicles[0].text
                else:
                    vehicle_text = "None"

                tasker = (
                    tasker_id,
                    self.scraper.find_nested_elements(tasker_div, ["tasker_info", "name"])[0].text,
                    vehicle_text, #Vehicles
                    self.scraper.find_attribute_of_nested_elements("src", self.scraper.find_nested_elements(tasker_div, ["tasker_info", "picture"])[0])
                )
                self.dbc.store_tasker(tasker)
                #self.scrape_reviews(tasker_id, tasker_div)

            # Store the fact that this tasker works in the current location
            if not self.dbc.tasker_location_exists(tasker_id, self.location_id):
                self.dbc.store_tasker_location([(tasker_id, self.location_id)])

            # Store the description of the tasker for THIS service
            if not self.dbc.description_exists(self.current_service, tasker_id):
                description = self.scraper.find_nested_elements(tasker_div, ["tasker_info", "description"])[0].text
                self.dbc.store_description([(description, self.current_service, tasker_id)])

            # Store number of tasks completed for this service
            if not self.dbc.completed_exists(self.current_service, tasker_id):
                if task_completion_info.startswith("No"):
                    no_completed_tasks = True
                else:
                    no_completed_tasks = False

                if not no_completed_tasks:
                    self.dbc.store_completed_tasks([
                        (tasker_id, self.current_service, task_completion_info.split(" Completed ")[0])])
                else:
                    self.dbc.store_completed_tasks([
                        (tasker_id, self.current_service, "0")])

            # Store price details
            if not self.dbc.price_details_exist(self.current_service, tasker_id):
                price_details = self.scraper.find_nested_elements(tasker_div, ["tasker_info", "price"])[0].text
                currency = price_details[0]
                amount = price_details.split("/")[0][1:]
                basis = price_details.split("/")[1][:2]

                self.dbc.store_price_details([(amount, currency, basis, tasker_id, self.current_service)])

            i += 1


    def scrape_reviews(self, tasker_id, tasker_div):

        reviews_button = self.scraper.find_nested_elements(tasker_div, ["tasker_info", "reviews_button"])[0]
        self.scraper.click_on_existing_element(reviews_button)
        review_page_next = self.scraper.find_elements(["tasker_info", "review_page_arrows"])

        if not review_page_next:
            self.scraper.click_on_element(["tasker_info", "reviews_close"])
            return
        else:
            review_page_next = review_page_next[1]

        review_content_htmls = []
        i = 0

        self.scraper.wait_till_visible(["tasker_info", "task_review_select"])
        task_review_select = self.scraper.find_nested_elements(tasker_div, ["tasker_info", "task_review_select"])[0]
        self.scraper.click_on_existing_element(task_review_select)

        task_review_all = self.scraper.find_nested_elements(tasker_div, ["tasker_info", "task_review_all"])[0]
        self.scraper.click_on_existing_element(task_review_all)

        while not self.scraper.find_attribute_of_nested_elements("disabled", review_page_next) == 'true':
            self.scraper.wait_till_visible(["tasker_info", "review_details", "rating_icon"])
            review_content = self.scraper.find_elements(["tasker_info", "review_page_content"])[0]
            review_content_html = self.scraper.find_attribute_of_nested_elements("innerHTML", review_content)
            review_content_htmls.append(review_content_html)
            self.scraper.click_on_existing_element(review_page_next)
            i += 1

        if self.scraper.find_elements(["tasker_info", "current_review_page"])[0].text == str(i + 1):
            review_content = self.scraper.find_elements(["tasker_info", "review_page_content"])[0]
            review_content_html = self.scraper.find_attribute_of_nested_elements("innerHTML", review_content)
            review_content_htmls.append(review_content_html)

        reviews = self.reviewExtractor.extract_reviews(tasker_id, review_content_htmls)
        self.dbc.store_reviews(reviews)
        self.scraper.click_on_element(["tasker_info", "reviews_close"])

    # Form filling functions
    def fill_interest_form(self):
        self.scraper.click_on_element(["task_interests", "just_browsing"])

    def fill_location_form(self):
        self.scraper.send_keys_to_element(["task_location", "street_address"], self.city + "," + self.location, True, True)
        self.scraper.send_keys_to_element(["task_location", "flat_number"], "", True, True)
        time.sleep(1)

    def fill_task_options_form(self):
        self.scraper.click_on_element(["task_size", "medium"])

        if self.scraper.find_elements(["vehicle_requirements", "not_needed"]):
            self.scraper.click_on_element(["vehicle_requirements", "not_needed"])

    def fill_details_form(self):
        self.scraper.send_keys_to_element(["details"], "Hi", True, True)

    def fill_items_form(self):
        self.scraper.click_on_element(["task_items", "both"])
        time.sleep(3)

    def fill_form_page(self, forms):
        for form in forms:
            self.formFunctions[form.text]()
            self.scraper.click_on_element(["continue_button"])

    # Main function
    def scrape_service(self, service, cities, start_location):

        #Variable used to skip till desired starting location
        not_started = True

        self.current_service = service[0]
        service_url = service[2]

        # Open service page form
        self.scraper.open_URL_as_page(service_url, "service_page")
        self.scraper.click_on_element(["find_help_button"])
        # Iterate all locations for the service
        for city in cities:
            self.city = city;
            for location in cities[city]:
                if start_location and (not location[1] == start_location) and not_started:
                    continue
                else:
                    not_started = False
                print("\tScraping " + location[1])
                self.location = location[1]
                self.location_id = location[0]
                self.scraper.change_current_page("task_description_page")

                # Find subforms in page and fill them
                forms = self.scraper.find_elements(["form_titles"])
                self.fill_form_page(forms)

                # Get the taskers
                self.scraper.change_current_page("tasker_listing_page")

                attempts = 0
                while self.iterate_days() == -1 and attempts < 4:
                    attempts += 1
                    if attempts == 4:
                        print("Service not scrapable")

                # Prepare next location scrape
                self.scraper.page_go_back()
                self.scraper.change_current_page("task_description_page")
                self.scraper.click_on_element(["task_interests", "icon"])

        self.scraper.finish()

