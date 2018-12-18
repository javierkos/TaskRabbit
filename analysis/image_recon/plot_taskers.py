import sqlite3
import matplotlib
matplotlib.use
import matplotlib.pyplot as plt
import numpy as np

def get_num_ethnicity(c):
    c.execute("SELECT ethnicity, COUNT(*) FROM "
              "tasker_img_predictions "
              "GROUP BY ethnicity;")
    ethnicities, count = zip(*list(c.fetchall()))
    return (ethnicities, count)

def get_num_gender(c):
    c.execute("SELECT gender, COUNT(*) FROM "
              "tasker_img_predictions "
              "GROUP BY gender;")
    genders, count = zip(*list(c.fetchall()))
    return (genders, count)

def get_average_price_by_ethnicity(c, service):

    c.execute("SELECT ethnicity, AVG(price_details.amount) FROM "
              "tasker_img_predictions, price_details "
              "WHERE tasker_img_predictions.tasker_id = price_details.tasker_id "
              "AND price_details.service_id = " + str(service) + " GROUP BY ethnicity;")
    ethnicities, av_prices = zip(*list(c.fetchall()))
    return (ethnicities, av_prices)

def get_median_price_by_ethnicity(c, service):
    c.execute("SELECT ethnicity, price_details.amount FROM "
              "tasker_img_predictions, price_details "
              "WHERE tasker_img_predictions.tasker_id = price_details.tasker_id "
              "AND price_details.service_id = " + str(service))
    ethnicity_dict = {"BLACK": [], "WHITE": [], "INDIA": [], "ASIAN": []}
    [ethnicity_dict[row[0]].append(row[1]) for row in c.fetchall()]
    return (list(ethnicity_dict.keys()), [np.median(ethnicity_dict[eth]) for eth in ethnicity_dict.keys()])

def get_median_price_by_gender(c, service):
    c.execute("SELECT gender, price_details.amount FROM "
              "tasker_img_predictions, price_details "
              "WHERE tasker_img_predictions.tasker_id = price_details.tasker_id "
              "AND price_details.service_id = " + str(service))
    gender_dict = {"Male": [], "Female": []}
    [gender_dict[row[0]].append(row[1]) for row in c.fetchall()]
    return (list(gender_dict.keys()), [np.median(gender_dict[eth]) for eth in gender_dict.keys()])

def get_all_age(c, service):
    c.execute("SELECT age, price_details.amount FROM "
              "tasker_img_predictions, price_details "
              "WHERE tasker_img_predictions.tasker_id = price_details.tasker_id "
              "AND price_details.service_id = " + str(service))
    ages, prices = zip(*list(c.fetchall()))
    return (ages, prices)

def get_all_moods(c, service):
    c.execute("SELECT mood, price_details.amount FROM "
              "tasker_img_predictions, price_details "
              "WHERE tasker_img_predictions.tasker_id = price_details.tasker_id "
              "AND price_details.service_id = " + str(service))
    moods, prices = zip(*list(c.fetchall()))
    return (moods, prices)


def get_all(c, service):
    c.execute("SELECT age, mood, ethnicity, gender, price_details.amount FROM "
              "tasker_img_predictions, price_details "
              "WHERE tasker_img_predictions.tasker_id = price_details.tasker_id "
              "AND price_details.service_id = " + str(service))
    ages, moods, ethnicitys, genders, prices = zip(*list(c.fetchall()))
    return (ages, moods, ethnicitys, genders, prices)

if __name__ == '__main__':

    conn = sqlite3.connect("../../databases/taskrabbit_los_angeles.db")
    c = conn.cursor()

    c.execute("SELECT service_id,name FROM services")

    plot_data = {service: get_average_price_by_ethnicity(c, service[0]) for service in c.fetchall()}

    fig_original = plt.figure(figsize=(10, 10))
    rows, columns = 3, 4
    colors = ["#1696d2", "#fdbf11", "#55b748", "#d2d2d2"]

    [fig_original.add_subplot(rows, columns, i + 1).bar(plot_data[service[0]][0], plot_data[service[0]][1], color=colors)
     for i, service in enumerate(plot_data.keys())]

    plt.show()

