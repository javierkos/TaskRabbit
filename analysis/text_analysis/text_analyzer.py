from nltk.sentiment.vader import SentimentIntensityAnalyzer as SIA
import requests
import time
import json
import sqlite3
import pandas as pd
import statsmodels.api as sm
from analysis.regression.data_prep import DataPreparation
import matplotlib
matplotlib.use
import matplotlib.pyplot as plt
import seaborn as sns


class TextAnalyzer:

    def __init__(self):
        #Define types of text analysis the class can do
        self.analysis_types = {
            "sentiment": self.get_sentiment,
            "correctness": self.get_correctness_per_char,
            "length": self.get_length
        }
        self.check_url = "https://languagetool.org/api/v2/check"
        self.sia = SIA()
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

    def get_length(self, X):
        return [len(text) for text in X]


conn = sqlite3.connect('../../databases/taskrabbit_ny.db')
c = conn.cursor()

df_data = {"text": [], "price": [], "vehicle": []}

c.execute("SELECT text, price_details.amount, taskers.vehicles FROM descriptions,taskers,services,price_details WHERE descriptions.tasker_id = taskers.tasker_id AND services.service_id = descriptions.service_id AND Taskers.tasker_id = price_details.tasker_id AND  price_details.service_id = services.service_id AND services.service_id = 1;")
for row in c.fetchall():
    df_data["text"].append(row[0])
    df_data["price"].append(row[1])
    df_data["vehicle"].append(0 if row[2] == "None" else 1)

df = pd.DataFrame(df_data, index=[i for i in range(0, len(df_data["text"]))])


ta = TextAnalyzer()
dp = DataPreparation()

res = ta.analyze(df["text"].values, ["sentiment", "length"])
df["sentiment"] = res["sentiment"]
df["length"] = res["length"]

y = df["price"]
X = df.drop("price", axis = 1).drop("text", axis = 1)

X = dp.scale_data(X)

fig1, ax1 = plt.subplots()
fig1.set_size_inches(16, 12)
plt.title("Correlation between variables for New York boroughs on service")
plt.gcf().subplots_adjust(bottom=0.35, left=0.35)
sns.heatmap(df.corr('kendall'),
            xticklabels=df.corr('kendall').columns.values,
            yticklabels=df.corr('kendall').columns.values)

plt.show()

av_price_vehicle = df.loc[df["vehicle"] == 1]["price"].mean()
av_price_novehicle = df.loc[df["vehicle"] == 0]["price"].mean()
print (av_price_vehicle)
print (av_price_novehicle)