import sqlite3
import sys
from analysis.text_analysis.text_analyzer import TextAnalyzer
import pickle

def percent_male(service_id, location_id):
   return 'SELECT ' \
          'COUNT(*)/(SELECT CAST(COUNT(*) AS FLOAT) ' \
              'FROM tasker_img_predictions, taskers , tasker_locations, price_details, services, locations ' \
              'WHERE taskers.tasker_id = tasker_img_predictions.tasker_id ' \
              'AND tasker_locations.tasker_id = taskers.tasker_id ' \
              'AND tasker_locations.location_id = locations.location_id ' \
              'AND price_details.service_id = services.service_id ' \
              'AND price_details.tasker_id = taskers.tasker_id ' \
              'AND services.service_id = ' + str(service_id) + ' ' \
              'AND locations.location_id = ' + str(location_id) + ') ' \
          'FROM tasker_img_predictions, taskers , tasker_locations, price_details, services, locations ' \
          'WHERE taskers.tasker_id = tasker_img_predictions.tasker_id ' \
          'AND tasker_locations.tasker_id = taskers.tasker_id ' \
          'AND tasker_locations.location_id = locations.location_id ' \
          'AND price_details.service_id = services.service_id ' \
          'AND price_details.tasker_id = taskers.tasker_id AND gender = "Male" ' \
          'AND services.service_id = ' + str(service_id) + ' ' \
          'AND locations.location_id = ' + str(location_id) + ' ' \
          'GROUP BY gender ;'

def percent_white(service_id, location_id):
   return 'SELECT ' \
          'COUNT(*)/(SELECT CAST(COUNT(*) AS FLOAT) ' \
              'FROM tasker_img_predictions, taskers , tasker_locations, price_details, services, locations ' \
              'WHERE taskers.tasker_id = tasker_img_predictions.tasker_id ' \
              'AND tasker_locations.tasker_id = taskers.tasker_id ' \
              'AND tasker_locations.location_id = locations.location_id ' \
              'AND price_details.service_id = services.service_id ' \
              'AND price_details.tasker_id = taskers.tasker_id ' \
              'AND services.service_id = ' + str(service_id) + ' ' \
              'AND locations.location_id = ' + str(location_id) + ') ' \
          'FROM tasker_img_predictions, taskers , tasker_locations, price_details, services, locations ' \
          'WHERE taskers.tasker_id = tasker_img_predictions.tasker_id ' \
          'AND tasker_locations.tasker_id = taskers.tasker_id ' \
          'AND tasker_locations.location_id = locations.location_id ' \
          'AND price_details.service_id = services.service_id ' \
          'AND price_details.tasker_id = taskers.tasker_id AND ethnicity = "WHITE" ' \
          'AND services.service_id = ' + str(service_id) + ' ' \
          'AND locations.location_id = ' + str(location_id) + ' ' \
          'GROUP BY ethnicity ;'

def median_age(service_id, location_id):
    return 1
    '''
    SELECT
    AVG(age)
    FROM(SELECT
    age
    FROM
    tasker_img_predictions, taskers, locations, services, price_details, tasker_locations
    WHERE
    tasker_img_predictions.tasker_id = taskers.tasker_id
    AND
    tasker_locations.tasker_id = taskers.tasker_id
    AND
    services.service_id = price_details.service_id
    AND
    price_details.tasker_id = price_details.tasker_id
    AND
    locations.location_id = tasker_locations.location_id
    ORDER
    BY
    age
    LIMIT
    2 - (SELECT COUNT( *)
    FROM
    tasker_img_predictions) % 2 - - odd
    1, even
    2
    OFFSET(SELECT(COUNT(*) - 1) / 2
    FROM
    tasker_img_predictions, taskers, locations, services, price_details, tasker_locations
    WHERE
    tasker_img_predictions.tasker_id = taskers.tasker_id
    AND
    tasker_locations.tasker_id = taskers.tasker_id
    AND
    services.service_id = price_details.service_id
    AND
    price_details.tasker_id = price_details.tasker_id
    AND
    locations.location_id = tasker_locations.location_id))
    '''

def avg_mood(service_id, location_id):
    return 'SELECT AVG(mood) ' \
           'FROM tasker_img_predictions, taskers, locations, services, price_details, tasker_locations ' \
           'WHERE tasker_img_predictions.tasker_id = taskers.tasker_id ' \
           'AND tasker_locations.tasker_id = taskers.tasker_id ' \
           'AND services.service_id = price_details.service_id ' \
           'AND price_details.tasker_id = price_details.tasker_id ' \
           'AND locations.location_id = tasker_locations.location_id ' \
           'AND services.service_id = ' +  str(service_id) + ' ' \
           'AND locations.location_id = ' + str(location_id) + ' '

def avg_sent_desc(service_id, location_id):
    return 'SELECT AVG("sentiment") FROM ' \
           '(SELECT descriptions.sentiment ' \
           'FROM taskers, locations, services, price_details, tasker_locations, descriptions ' \
           'WHERE tasker_locations.tasker_id = taskers.tasker_id ' \
           'AND descriptions.service_id = services.service_id ' \
           'AND locations.location_id = tasker_locations.location_id ' \
           'AND descriptions.tasker_id = taskers.tasker_id ' \
           'AND services.service_id = ' + str(service_id) + ' ' \
           'AND locations.location_id = ' + str(location_id) + ' ' \
           'GROUP BY descriptions.description_id)'

def avg_errors_desc(service_id, location_id):
    return 'SELECT AVG("errors_per_word") FROM ' \
           '(SELECT descriptions.errors_per_word ' \
           'FROM taskers, locations, services, price_details, tasker_locations, descriptions ' \
           'WHERE tasker_locations.tasker_id = taskers.tasker_id ' \
           'AND descriptions.service_id = services.service_id ' \
           'AND locations.location_id = tasker_locations.location_id ' \
           'AND descriptions.tasker_id = taskers.tasker_id ' \
           'AND services.service_id = ' + str(service_id) + ' ' \
           'AND locations.location_id = ' + str(location_id) + ' ' \
           'GROUP BY descriptions.description_id)'

def get_texts_desc(service_id, location_id):
    return 'SELECT distinct descriptions.description_id, descriptions.text ' \
           'FROM taskers, locations, services, price_details, tasker_locations, descriptions ' \
           'WHERE tasker_locations.tasker_id = taskers.tasker_id ' \
           'AND descriptions.service_id = services.service_id ' \
           'AND locations.location_id = tasker_locations.location_id ' \
           'AND descriptions.tasker_id = taskers.tasker_id ' \
           'AND services.service_id = ' + str(service_id) + ' ' \
           'AND locations.location_id = ' + str(location_id) + ''

def extract_data(dct):
    string = ""
    keys = [key for key in dct.keys()]
    for i, key in enumerate(keys):
        string += str(dct[key])
        if not i == (len(keys) - 1):
            string += ", "
    print (string)
    return string

if __name__ == '__main__':

    conn = sqlite3.connect('../databases/' + sys.argv[2])
    c = conn.cursor()
    c2 = conn.cursor()
    c3 = conn.cursor()

    services = [row[0] for row in c.execute("SELECT service_id FROM services").fetchall()]
    if sys.argv[1] == "per_tasker":
        pass
    else:

        var_dct = {
            "percent_male": percent_male,
            "percent_white": percent_white,
            "avg_mood": avg_mood,
            "avg_errors_per_words_desc": avg_errors_desc,
            "avg_sentiment_desc": avg_sent_desc,
        }
        for service in services:
            loc_dct = {}
            for loc_row in c.execute("SELECT location_id FROM locations").fetchall():
                try:
                    loc_dct[loc_row[0]] = {
                        key: c.execute(var_dct[key](service, loc_row[0])).fetchone()[0] for key in var_dct.keys()
                    }
                    c3.execute("INSERT INTO service_location_data "
                               "VALUES(" + str(service) + ", " + str(loc_row[0]) + ", " + extract_data(
                        loc_dct[loc_row[0]]) + ")")
                except Exception as e:
                    print (e)
                    print (loc_dct)
                    print (loc_row)

                conn.commit()

    '''
    ta = TextAnalyzer()
    
    services = [row[0] for row in c.execute("SELECT service_id FROM services").fetchall()]




    descriptions = [row for row in c.execute("SELECT descriptions.description_id, descriptions.text FROM descriptions").fetchall()]
    ids, texts = zip(*descriptions)

    res = ta.analyze(texts, ["sentiment", "correctness"])

    tot_ids = len(ids)
    for i in range(0, len(ids)):
        c2.execute("UPDATE descriptions SET sentiment = " +
                   str(res["sentiment"][i]) +
                   ", errors_per_word = " +
                   str(res["correctness"][i]) + " WHERE description_id = " + str(ids[i]))
    conn.commit()

    print (tot_ids)
    '''












