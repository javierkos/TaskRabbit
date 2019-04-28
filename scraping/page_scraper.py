import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

chrome_options = Options()

class PageScraper:

	#Time to wait after page openings and clicks
	wait_time = 1

	def __init__(self, pages, main_url):
		self.main_url = main_url
		self.pages = pages
		self.driver = webdriver.Chrome(executable_path=r'/usr/bin/chromedriver', chrome_options=chrome_options)
		self.wait = WebDriverWait(self.driver, 10)
		self.driver.get(self.main_url)

	#Change current page without having to open a new url
	def change_current_page(self, key):
		for page in self.pages:
			if page["name"] == key:
				self.current_page = page

	#Open one of the pages passed to the class
	def open_page(self, key):
		for page in self.pages:
			if page["name"] == key:
				self.driver.get(self.main_url + page["url"])
				self.current_page = page
				time.sleep(self.wait_time)
				return

	#Open a url and "let it be" one of the pages passed to the class
	def open_URL_as_page(self, url, key):
		for page in self.pages:
			if page["name"] == key:
				self.driver.get(url)
				self.current_page = page
				return

	def get_source(self):
		return self.driver.page_source

	#Find elements
	def find_elements(self, keyPath):
		temp_selector = self.current_page
		for key in keyPath:
			temp_selector = temp_selector[key]

		try:
			self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, temp_selector)))
		except TimeoutException:
			return None
		return self.driver.find_elements_by_css_selector(temp_selector)

	#Find elements starting from an already existing element
	def find_nested_elements(self, startElement, keyPath):
		temp_selector = self.current_page
		for key in keyPath:
			temp_selector = temp_selector[key]
		
		return startElement.find_elements_by_css_selector(temp_selector)

	def find_attribute_of_elements(self, attribute, elementKey):
		elements = self.driver.find_elements_by_css_selector(self.current_page[elementKey])
		attribute_data = []
		for element in elements:
			attribute_data.append(element.get_attribute(attribute))
		return attribute_data

	def find_attribute_of_nested_elements(self, attribute, element):
		return element.get_attribute(attribute)

	#Click on an element found by traversing the current page through an array of keys
	def click_on_element(self, keyPath):
		temp_selector = self.current_page
		for key in keyPath:
			temp_selector = temp_selector[key]

		element = self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, temp_selector)))
		element.click()

	#Click on an element
	def click_on_existing_element(self, element):
		element.click()
		time.sleep(self.wait_time)

	#Send keys to an element found by traversing the current page through an array of keys
	def send_keys_to_element(self, keyPath, data, withEnter, clearBefore):
		temp_selector = self.current_page
		for key in keyPath:
			temp_selector = temp_selector[key]

		element = self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, temp_selector)))
		if clearBefore:
			element.click()
			self.driver.execute_script("arguments[0].select();", element)
			element.send_keys(Keys.BACKSPACE)
		element.send_keys(data) if withEnter else element.send_keys(data + "\n")

	#Return elements in a particular level (reached by following an array of keys)
	def get_nested_elements(self, keyPath):
		temp_selector = self.current_page
		for key in keyPath:
			temp_selector = temp_selector[key]
		nested_elements = []
		for element in temp_selector:
			nested_elements.append(element)
		return nested_elements

	def wait_till_visible(self, keyPath):
		temp_selector = self.current_page
		for key in keyPath:
			temp_selector = temp_selector[key]
		self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, temp_selector)))

	def page_go_back(self):
		self.driver.execute_script("window.history.go(-1)")

	def safe_element_click(self, element):
		webdriver.ActionChains(self.driver).move_to_element(element).click(element).perform()

	def finish(self):
		self.driver.close()
		self.driver.quit()