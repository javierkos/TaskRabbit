import os
from bs4 import BeautifulSoup
#from rejson import Client, Path
import json

#rj = Client(host='localhost', port=6379)

'''
	Extracts review data from downloaded html source and adds it to the users json file
'''

class ReviewExtractor:

	def __init__(self):
		# Start scraper
		print ("Start extracting reviews")

	def extract_reviews(self, tasker_id, review_content_htmls):

		reviews = []

		# For each review page
		for review_content_html in review_content_htmls:

			soup = BeautifulSoup(review_content_html, 'html.parser')
			reviews_html = soup.select(".tasker-review")
			for review_html in reviews_html:
				title = review_html.select(".media--content")[0].select("strong")[0].text

				rating_element = review_html.select(".reviews-section--tasker-rating>li")
				'''				
				rating_element = review_html.select("")
				if 'ss-rkt-thumbup' in rating_element["class"]:
					rating = "positive"
				elif 'ss-rkt-thumbdown' in rating_element["class"]:
					rating = "negative"
				else:
					rating = "None"
				'''

				review = (
					review_html.select(".exterior__bottom--sm")[0].text, #Text
					review_html.select(".muted")[0].text.split("- ")[1], #Date
					str(len(rating_element)), #Rating
					tasker_id,
					title
				)

				reviews.append(review)

		return reviews