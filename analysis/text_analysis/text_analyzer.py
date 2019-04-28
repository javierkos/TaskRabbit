import requests
import time
import json
import enchant
import re
import sqlite3
import pandas as pd
import statsmodels.api as sm
from analysis.regression.data_prep import DataPreparation
from nltk.sentiment.vader import SentimentIntensityAnalyzer as SIA

class TextAnalyzer:

    def __init__(self):
        #Define types of text analysis the class can do
        self.analysis_types = {
            "sentiment": self.get_sentiment,
            "correctness": self.get_errors_per_char,
            "length": self.get_length
        }
        self.check_url = "https://languagetool.org/api/v2/check"
        self.sia = SIA()
        self.d = enchant.Dict("en_US")
    def analyze(self, X, targets = ["sentiment"]):
        return {target: self.analysis_types[target](X) for target in targets}

    def get_sentiment(self, X):
        return [self.sia.polarity_scores(text)["compound"] for text in X]

    def get_correctness_per_char(self, X):
        ret = []
        i = 1
        for text in X:
            if i % 15 == 0:
                time.sleep(60)
            r = requests.post(self.check_url, data={'text': text, 'language': 'en-US'})
            ret.append(len(json.loads(r.text)["matches"])/len(text))
            i += 1
        return ret

    def getWords(self, text):
        return re.compile('\w+').findall(text)

    def get_errors_per_char(self, X):
        ret = []
        for text in X:
            words = self.getWords(text)
            try:
                ret.append(sum(0 if self.d.check(word) else 1 for word in words)/len(words))
            except Exception:
                ret.append(0.5)
        return ret

    def get_length(self, X):
        return [len(text) for text in X]