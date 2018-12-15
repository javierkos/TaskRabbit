import pandas as pd
import sqlite3
import sys
import numpy as np
import matplotlib
matplotlib.use
import matplotlib.pyplot as plt
from matplotlib import rcParams
import pickle
import seaborn as sns
import statistics
from nltk.sentiment.vader import SentimentIntensityAnalyzer as SIA
'''
    Takes in two params:
    1st - name (key) of city
    2nd - name of db
'''
if __name__ == '__main__':
    if len(sys.argv[1:]) == 0:
        raise Exception("No arguments passed - aborting...")

    conn = sqlite3.connect('../databases/' + sys.argv[2])
    conn2 = sqlite3.connect('../databases/' + sys.argv[2])

    c = conn.cursor()
    c2 = conn2.cursor()

    dfs = {

    }
    services = [1, 2, 3, 4, 6, 7, 8, 29, 30, 35, 51, 52]
    i = 0
    sia = SIA()
    for service in services:
        print(i)

        c2.execute("SELECT name FROM services WHERE services.service_id = " + str(service))
        service_name = c2.fetchone()[0]

        c.execute(
            "SELECT * FROM location_demographics INNER JOIN tasker_locations ON location_demographics.location_id = tasker_locations.location_id  INNER JOIN price_details ON tasker_locations.tasker_id = price_details.tasker_id WHERE price_details.service_id = " + str(
                service))

        locations = {

        }
        for row in c:
            if not row[0] in locations.keys():
                c2.execute(
                    "SELECT descriptions.text FROM price_details INNER JOIN services ON price_details.service_id = services.service_id INNER JOIN taskers ON price_details.tasker_id = taskers.tasker_id INNER JOIN tasker_locations ON taskers.tasker_id = tasker_locations.tasker_id INNER JOIN descriptions ON taskers.tasker_id = descriptions.tasker_id WHERE services.service_id = " + str(
                        service) + " AND tasker_locations.location_id = " + str(
                        row[0]) + " AND descriptions.service_id = " + str(service) + "")

                sentiments = []
                tot_sentiment = 0
                for desc in c2:
                    sentiments.append(sia.polarity_scores(desc[0])['compound'])

                locations[row[0]] = {}
                locations[row[0]]["costs"] = []
                locations[row[0]]['av. desc. sentiment'] = statistics.mean(sentiments)
                locations[row[0]]["pop_density"] = row[2]
                locations[row[0]]["median_age"] = row[3]
                locations[row[0]]["percent_highschool_plus"] = row[4]
                locations[row[0]]["homeownership_rate"] = row[5]
                locations[row[0]]["median_household_income"] = row[6]
                locations[row[0]]["percent_foreign_born"] = row[7]
                locations[row[0]]["percent_below_poverty"] = row[8]
                locations[row[0]]["crime"] = row[9]
                locations[row[0]]["per_white"] = row[10]
                locations[row[0]]["unemployment"] = row[11]
                locations[row[0]]["median_rent"] = row[12]
            locations[row[0]]["costs"] = locations[row[0]]["costs"] + [row[16]]


        pop_density = []
        median_age = []
        percent_highschool_plus = []
        housing_units = []
        median_household_income = []
        percent_foreign_born = []
        percent_below_poverty = []
        crime = []
        per_white = []
        sentiment = []
        unemployment = []
        median_rent = []
        cost = []
        serv = []
        for location in locations.keys():
            serv.append(service)
            pop_density.append(locations[location]["pop_density"])
            median_age.append(locations[location]["median_age"])
            percent_highschool_plus.append(locations[location]["percent_highschool_plus"])
            housing_units.append(locations[location]["homeownership_rate"])
            median_household_income.append(locations[location]["median_household_income"])
            percent_foreign_born.append(locations[location]["percent_foreign_born"])
            percent_below_poverty.append(locations[location]["percent_below_poverty"])
            crime.append(locations[location]["crime"])
            per_white.append(locations[location]["per_white"])
            unemployment.append(locations[location]["unemployment"])
            median_rent.append(locations[location]["median_rent"])
            sentiment.append(locations[location]['av. desc. sentiment'])
            cost.append(statistics.median(locations[location]["costs"]))

        vars = []
        vars.append(pop_density)
        vars.append(median_age)
        vars.append(percent_highschool_plus)
        vars.append(housing_units)
        vars.append(median_household_income)
        vars.append(percent_foreign_born)
        vars.append(percent_below_poverty)
        vars.append(cost)
        # print (np.corrcoef(vars))

        # plt.scatter(cost, pop_density)
        # plt.show()

        df = pd.DataFrame({'Pop. density': pop_density,
                           # 'Median age': median_age,
                           'Highschool': percent_highschool_plus,
                           'Homeownership rate': housing_units,
                           'Median household income': median_household_income,
                           'Percent. foreign born': percent_foreign_born,
                           'Percent. below poverty': percent_below_poverty,
                           'Crime rate': crime,
                           'Per. white': per_white,
                           'Unemployment rate': unemployment,
                           'Median rent': median_rent,
                           'Av. desc. sentiment': sentiment,
                           'Median service cost': cost})

        i += 1
        dfs[service_name] = df

    for service in dfs.keys():
        with open("dataframes/" + sys.argv[1] + "/" + service + ".pkl", "wb") as output_file:
            pickle.dump(dfs[service], output_file)