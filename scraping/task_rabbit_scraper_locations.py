from page_data import pages
from page_scraper import PageScraper
import os
from multiprocessing import Pool, cpu_count
from itertools import repeat
import time
import os.path
import json
from selenium.common.exceptions import WebDriverException
from task_rabbit_extractor import ReviewExtractor
import sqlite3
from database_caller import DatabaseCaller


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
        self.scraper.changeCurrentPage("services_page")
        try:
            self.scraper.clickOnElement(["cookie_dismiss_button"])
        except Exception as e:
            print ("No cookie message, continue...")

        # Form filling function switcher
        self.formFunctions = {
            "TASK INTEREST": self.fillInterestForm,
            "YOUR TASK LOCATION": self.fillLocationForm,
            "START ADDRESS": self.fillLocationForm,
            "END ADDRESS (OPTIONAL)": self.fillLocationForm,
            "TASK OPTIONS": self.fillTaskOptionsForm,
            "TELL US THE DETAILS OF YOUR TASK": self.fillDetailsForm,
            "YOUR ITEMS": self.fillItemsForm
        }

    def iterate_days(self):
        days = self.scraper.findElements(["days"])

        #If view type is the day scroller
        if not days == None:
            day_scroller = self.scraper.findElements(["days_scroller"])
            i = 0
            for day in days:
                print (day.text)
                try:
                    self.scraper.clickOnExistingElement(day)
                except WebDriverException:
                    self.scraper.clickOnExistingElement(day_scroller[0])
                    self.scraper.clickOnExistingElement(day)

                self.get_taskers()
                i += 1
        #If view type is the day selector
        else:
            choose_day_buton = self.scraper.findElements(["choose_day_button"])
            if choose_day_buton:
                choose_day_buton = self.scraper.findElements(["choose_day_button"])[0]
            else:
                return -1
            self.scraper.clickOnExistingElement(choose_day_buton)
            day_buttons = self.scraper.findElements(["calendar_days_available"])
            self.scraper.clickOnExistingElement(day_buttons[1])
            self.scraper.clickOnExistingElement(day_buttons[-1])
            apply_changes = self.scraper.findElements(["apply_calendar_choice"])[0]
            self.scraper.safe_element_click(apply_changes)

            self.get_taskers()


    def get_taskers(self):

        time.sleep(2)
        tasker_divs = self.scraper.findElements(["tasker_results"])

        #If no tasker results
        if tasker_divs == None:
            return

        #For every tasker
        i = 0
        total = len (tasker_divs)
        for tasker_div in tasker_divs:

            try:
                task_completion_info = self.scraper.findNestedElements(tasker_div, ["tasker_info", "completed_tasks"])[
                0].text
            except Exception:
                continue
                print ("STALE ELEMENT EXCEPTION")

            tasker_id = self.scraper.findAttributeOfNestedElements("data-user-id", tasker_div)
            # If tasker doesnt exist, scrape and store reviews.
            if not self.dbc.tasker_exists(tasker_id):
                #Vehicles
                vehicles = self.scraper.findNestedElements(tasker_div, ["tasker_info", "vehicles"])
                if vehicles:
                    vehicle_text = vehicles[0].text
                else:
                    vehicle_text = "None"

                tasker = (
                    tasker_id,
                    self.scraper.findNestedElements(tasker_div, ["tasker_info", "name"])[0].text, #Name
                    vehicle_text, #Vehicles
                    self.scraper.findAttributeOfNestedElements("src",
                                                               self.scraper.findNestedElements(tasker_div, [
                                                                   "tasker_info", "picture"])[0])
                )
                self.dbc.store_tasker(tasker)
                #self.scrapeReviews(tasker_id, tasker_div)

            # Store the fact that this tasker works in the current location
            if not self.dbc.tasker_location_exists(tasker_id, self.location_id):
                self.dbc.store_tasker_location([(tasker_id, self.location_id)])

            # Store the description of the tasker for THIS service
            if not self.dbc.description_exists(self.current_service, tasker_id):
                description = self.scraper.findNestedElements(tasker_div, ["tasker_info", "description"])[0].text
                self.dbc.store_description([(description, self.current_service, tasker_id)])

            # Store number of tasks completed for this service
            if not self.dbc.completed_exists(self.current_service, tasker_id):
                if task_completion_info.startswith("No"):
                    no_completed_tasks = True
                else:
                    no_completed_tasks = False

                if not no_completed_tasks:
                    self.dbc.storeCompletedTasks([
                        (tasker_id, self.current_service, task_completion_info.split(" Completed ")[0])])
                else:
                    self.dbc.storeCompletedTasks([
                        (tasker_id, self.current_service, "0")])

            # Store price details
            if not self.dbc.price_details_exist(self.current_service, tasker_id):
                price_details = self.scraper.findNestedElements(tasker_div, ["tasker_info", "price"])[0].text
                currency = price_details[0]
                amount = price_details.split("/")[0][1:]
                basis = price_details.split("/")[1][:2]

                self.dbc.storePriceDetails([(amount, currency, basis, tasker_id, self.current_service)])

            i += 1


    def scrapeReviews(self, tasker_id, tasker_div):

        reviews_button = self.scraper.findNestedElements(tasker_div, ["tasker_info", "reviews_button"])[0]
        self.scraper.clickOnExistingElement(reviews_button)
        review_page_next = self.scraper.findElements(["tasker_info", "review_page_arrows"])

        if not review_page_next:
            self.scraper.clickOnElement(["tasker_info", "reviews_close"])
            return
        else:
            review_page_next = review_page_next[1]

        review_content_htmls = []
        i = 0

        self.scraper.waitTillVisible(["tasker_info", "task_review_select"])
        task_review_select = self.scraper.findNestedElements(tasker_div, ["tasker_info", "task_review_select"])[0]
        self.scraper.clickOnExistingElement(task_review_select)

        task_review_all = self.scraper.findNestedElements(tasker_div, ["tasker_info", "task_review_all"])[0]
        self.scraper.clickOnExistingElement(task_review_all)

        while not self.scraper.findAttributeOfNestedElements("disabled", review_page_next) == 'true':
            self.scraper.waitTillVisible(["tasker_info", "review_details", "rating_icon"])
            review_content = self.scraper.findElements(["tasker_info", "review_page_content"])[0]
            review_content_html = self.scraper.findAttributeOfNestedElements("innerHTML", review_content)
            review_content_htmls.append(review_content_html)
            self.scraper.clickOnExistingElement(review_page_next)
            i += 1

        if self.scraper.findElements(["tasker_info", "current_review_page"])[0].text == str(i + 1):
            review_content = self.scraper.findElements(["tasker_info", "review_page_content"])[0]
            review_content_html = self.scraper.findAttributeOfNestedElements("innerHTML", review_content)
            review_content_htmls.append(review_content_html)

        reviews = self.reviewExtractor.extract_reviews(tasker_id, review_content_htmls)
        self.dbc.storeReviews(reviews)
        self.scraper.clickOnElement(["tasker_info", "reviews_close"])

    # Form filling functions
    def fillInterestForm(self):
        self.scraper.clickOnElement(["task_interests", "just_browsing"])

    def fillLocationForm(self):
        self.scraper.sendKeysToElement(["task_location", "street_address"], self.city + "," + self.location, True, True)
        self.scraper.sendKeysToElement(["task_location", "flat_number"], "", True, True)
        time.sleep(1)

    def fillTaskOptionsForm(self):
        self.scraper.clickOnElement(["task_size", "medium"])

        if self.scraper.findElements(["vehicle_requirements", "not_needed"]):
            self.scraper.clickOnElement(["vehicle_requirements", "not_needed"])

    def fillDetailsForm(self):
        self.scraper.sendKeysToElement(["details"], "Hi", True, True)

    def fillItemsForm(self):
        self.scraper.clickOnElement(["task_items", "both"])
        time.sleep(3)

    def fillFormPage(self, forms):
        for form in forms:
            self.formFunctions[form.text]()
            self.scraper.clickOnElement(["continue_button"])

    # Main function
    def scrapeService(self, service, cities, start_location):

        #Variable used to skip till desired starting location
        not_started = True

        self.current_service = service[0]
        service_url = service[2]

        # Open service page form
        self.scraper.openURLAsPage(service_url, "service_page")
        self.scraper.clickOnElement(["find_help_button"])
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
                self.scraper.changeCurrentPage("task_description_page")

                # Find subforms in page and fill them
                forms = self.scraper.findElements(["form_titles"])
                self.fillFormPage(forms)

                # Get the taskers
                self.scraper.changeCurrentPage("tasker_listing_page")

                attempts = 0
                while self.iterate_days() == -1 and attempts < 4:
                    attempts += 1
                    if attempts == 4:
                        print("Service not scrapable")

                # Prepare next location scrape
                self.scraper.pageGoBack()
                self.scraper.changeCurrentPage("task_description_page")
                self.scraper.clickOnElement(["task_interests", "icon"])

        self.scraper.finish()

