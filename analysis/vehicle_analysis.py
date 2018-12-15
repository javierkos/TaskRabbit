import sqlite3
import pandas as pd
import matplotlib
matplotlib.use
import matplotlib.pyplot as plt
import sys

'''
    Some analysis on the relationship between price and the number of vehicles taskers have
'''

if __name__ == '__main__':
    conn = sqlite3.connect('databases/' + sys.argv[1])
    c = conn.cursor()

    c.execute("SELECT service_id, name FROM services;")

    services = [(row[0], row[1]) for row in c.fetchall()]

    av_prices_vehicle = {
        "0": [],
        "1": [],
        "2+": []
    }

    diffs = []
    for service in services:
        df_data = {"price": [], "vehicle": []}

        c.execute("SELECT price_details.amount, taskers.vehicles FROM descriptions,taskers,services,price_details WHERE descriptions.tasker_id = taskers.tasker_id AND services.service_id = descriptions.service_id AND Taskers.tasker_id = price_details.tasker_id AND  price_details.service_id = services.service_id AND services.service_id = " + str(service[0]) + ";")
        for row in c.fetchall():
            df_data["price"].append(row[0])
            df_data["vehicle"].append(0 if row[1] == "None" else len(row[1].split("Vehicle: ")[0].split(",")))

        df = pd.DataFrame(df_data, index=[i for i in range(0, len(df_data["price"]))])

        y = df["price"]
        X = df.drop("price", axis=1)

        no_vehicle = df.loc[df["vehicle"] == 0]["price"].median()
        one_vehicle = df.loc[df["vehicle"] == 1]["price"].median()
        more_vehicle = df.loc[df["vehicle"] > 1]["price"].median()

        av_prices_vehicle["0"].append(no_vehicle)
        av_prices_vehicle["1"].append(one_vehicle)
        av_prices_vehicle["2+"].append(more_vehicle)

        diffs.append((df.loc[df["vehicle"] > 0]["price"].median() - no_vehicle)/no_vehicle * 100)


    av_diff = '%1.2f' % (sum(diffs)/len(diffs))
    
    #Table to show percentage increase in median price of services when using vehicles
    fig, ax = plt.subplots()
    ax.axis('off')
    ax.axis('tight')
    plt.title("Increase in percentage of median price where vehicle used by taskers")
    df = pd.DataFrame([[service[1], '%1.2f' % diffs[i]] for i, service in enumerate(services)] + [["Average", av_diff]], columns= ["Service", "Per. increase in median price (%)"])

    t = ax.table(cellText=df.values, colLabels=df.columns, loc='center', cellLoc='center')

    t._cells[(0, 0)].set_facecolor("#4CA6CD")
    t._cells[(0, 1)].set_facecolor("#4CA6CD")
    t._cells[(df.shape[0], 0)].set_facecolor("#B0E0E6")
    t._cells[(df.shape[0], 1)].set_facecolor("#B0E0E6")

    fig.tight_layout()
    fig.set_size_inches(16, 12)
    plt.savefig("analysis/plots/vehicle_analysis/" + sys.argv[2] + "/increase_in_price.png")

    #Plot difference in median price between having no vehicle, having one, or having more than one for every service
    fig, ax = plt.subplots()
    plt.title("Difference in median price of services between not having different number of vehicles")
    df_plot = pd.DataFrame(av_prices_vehicle, [service[1] if len(service[1]) < 15 else service[1][:12] + "..." for service in services])
    df_plot.plot(kind='bar', fig=fig, ax=ax)
    plt.xticks(rotation=25)
    fig.set_size_inches(16, 12)
    plt.savefig("analysis/plots/vehicle_analysis/" + sys.argv[2] + "/difference_median_price.png")
