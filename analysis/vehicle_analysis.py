import sqlite3
import pandas as pd
import matplotlib
matplotlib.use
import matplotlib.pyplot as plt
import sys
import numpy as np

''' Some analysis on the relationship between price and the number of vehicles taskers have 
    
    Args:
            - Argument_1: name of the database to gather data from    
'''

if __name__ == '__main__':
    # Connect to database passed as argument
    conn = sqlite3.connect('../databases/' + sys.argv[1])
    c = conn.cursor()

    # Get service list
    c.execute("SELECT service_id, name FROM services;")
    services = [(row[0], row[1]) for row in c.fetchall()]

    # Average prices for eac
    av_prices_vehicle = {"0": [], "1": [], "2+": []}

    # For each service, find the percentage increase in median price when vehicles used
    diffs = []
    for service in services:
        df_data = {"price": [], "vehicle": []}

        # Get price and number of vehicles for each tasker
        c.execute("SELECT price_details.amount, taskers.vehicles FROM descriptions,taskers,services,price_details "
                  "WHERE descriptions.tasker_id = taskers.tasker_id AND services.service_id = descriptions.service_id "
                  "AND Taskers.tasker_id = price_details.tasker_id AND  price_details.service_id = services.service_id "
                  "AND services.service_id = " + str(service[0]) + ";")
        for row in c.fetchall():
            df_data["price"].append(row[0])
            df_data["vehicle"].append(0 if row[1] == "None" else len(row[1].split("Vehicle: ")[0].split(",")))

        # Create dataframe
        df = pd.DataFrame(df_data, index=[i for i in range(0, len(df_data["price"]))])

        # Find median price for each number of vehicles
        no_vehicle = df.loc[df["vehicle"] == 0]["price"].median()
        one_vehicle = df.loc[df["vehicle"] == 1]["price"].median()
        more_vehicle = df.loc[df["vehicle"] > 1]["price"].median()

        av_prices_vehicle["0"].append(no_vehicle)
        av_prices_vehicle["1"].append(one_vehicle)
        av_prices_vehicle["2+"].append(more_vehicle)

        #Percentage change
        diffs.append((df.loc[df["vehicle"] > 0]["price"].median() - no_vehicle)/no_vehicle * 100)


    # Average percentage change
    av_diff = '%1.2f' % (sum(diffs)/len(diffs))
    
    # Table to show percentage increase in median price of services when using vehicles
    fig, ax = plt.subplots()
    ax.axis('off'), ax.axis('tight')
    plt.title("Increase in percentage of median price where vehicle used by taskers")
    df = pd.DataFrame([[service[1], '%1.2f' % diffs[i]] for i, service in enumerate(services)] +
                      [["Average", av_diff]], columns= ["Service", "Per. increase in median price (%)"])
    t = ax.table(cellText=df.values, colLabels=df.columns, loc='center', cellLoc='center')


    # Plot difference in median price between having no vehicle, having one, or having more than one for every service
    fig, ax = plt.subplots()
    plt.title("Difference in median price of services between not having different number of vehicles")
    df_plot = pd.DataFrame(av_prices_vehicle, [service[1] if len(service[1]) < 15 else service[1][:12] + "..."
                                               for service in services])
    df_plot.plot(kind='bar', fig=fig, ax=ax)
    plt.xticks(rotation=25)
    fig.set_size_inches(16, 12)
    la, sf, ny = [4, 9, 2], [1, 2, 3], [11, 12, 13]
    cities = ["LA", "SF", "NY"]
    pos = np.arange(3)
    ax = plt.subplot(111)
    ax.bar(pos, la, width=0.2, align='center')
    ax.bar(pos + 0.2, sf, width=0.2, align='center')
    ax.bar(pos + 0.4, ny, width=0.2, align='center')

    #Show plots
    plt.show()
