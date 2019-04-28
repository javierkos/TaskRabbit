import pandas as pd
import os
import pickle
import sys
import json
from analysis.image_recon.image_test_service import ImageTestService


'''
    Used to either create a dataframe from the datasets of images or call the ImageTestService class.
    Pass 1 additional argument when running script, which is action type:
        - if "store", then program will create the dataframe from the folder of UTKFace images
        
        - if "test", the dataframe will be loaded and tested against a service  
'''
def store_dataframe():
    X = pd.DataFrame(columns=['f_name', 'age', 'gender', 'race'])

    i = 0
    for filename in os.listdir('test_datasets/UTKFace'):
        features = filename.split("_")
        X.loc[i] = [filename, features[0], features[1], features[2]]
        i += 1
    print (X.loc[0])
    with open("test_datasets/UTK_df.pkl", "wb") as df_file:
        pickle.dump(X, df_file)

def test_slightcorp():
    with open("test_datasets/UTK_df.pkl", "rb") as df_file:
        X = pickle.load(df_file)
    its = ImageTestService(X.sample(250))
    its.test_slightcorp()

def test_faceplusplus():
    with open("test_datasets/UTK_df.pkl", "rb") as df_file:
        X = pickle.load(df_file)
    its = ImageTestService(X.sample(500))
    its.test_faceplusplus()

def get_slightcorp_genre(genre_score):
    return "1" if genre_score > 0 else "0"

def get_faceplusplus_genre(genre_score):
    return "1" if genre_score == "Female" else "0"

def get_slightcorp_ethnicity(ethnicity):
    dct = {
        "white": ["0"],
        "black": ["1"],
        "asian": ["2"],
        "other": ["3", "4"]
    }
    return dct[ethnicity]

def get_faceplusplus_ethnicity(ethnicity):
    dct = {
        "WHITE": ["0"],
        "BLACK": ["1"],
        "ASIAN": ["2"],
        "INDIA": ["3", "4"]
    }
    return dct[ethnicity]

def mse_age(result_dict):
    tot = 0
    for result in result_dict[:-1]:
        sq = (int(result["actual_age"]) - result["predicted_age"]) ** 2
        tot += sq
    return tot/len(result_dict[:-1])

def score_slightcorp():
    with open("results/slightcorp.json", "r") as read_file:
        slightcorp_res = json.load(read_file)
    gender_score = sum([1 if person["actual_genre"] == get_slightcorp_genre(int(person["predicted_genre"]))
                        else 0 for person in slightcorp_res[:-1]])

    ethnicity_score = sum([1 if person["actual_ethnicity"] in get_slightcorp_ethnicity(person["predicted_ethnicity"])
                        else 0 for person in slightcorp_res[:-1]])

    age_score = mse_age(slightcorp_res)

    return {
        "gender_score_unfailed": '%1.2f' % (gender_score / len(slightcorp_res[:-1]) * 100),
        "gender_scoe_with_fails": '%1.2f' % (gender_score / (len(slightcorp_res[:-1]) + int(slightcorp_res[-1][0])) * 100),
        "ethnicity_score_unfailed": '%1.2f' % (ethnicity_score / len(slightcorp_res[:-1]) * 100),
        "ethnicity_score_with_fails": '%1.2f' % (ethnicity_score / (len(slightcorp_res[:-1]) + int(slightcorp_res[-1][0])) * 100),
        "age_score": '%1.2f' % age_score
    }

def score_faceplusplus():
    with open("results/faceplusplus.json", "r") as read_file:
        faceplusplus_res = json.load(read_file)
    gender_score = sum([1 if person["actual_gender"] == get_faceplusplus_genre(person["predicted_gender"])
                        else 0 for person in faceplusplus_res[:-1]])

    ethnicity_score = sum([1 if person["actual_ethnicity"] in get_faceplusplus_ethnicity(person["predicted_ethnicity"])
                        else 0 for person in faceplusplus_res[:-1]])

    age_score = mse_age(faceplusplus_res)

    return {
        "gender_score_unfailed": '%1.2f' % (gender_score / len(faceplusplus_res[:-1]) * 100),
        "gender_score_with_fails": '%1.2f' % (gender_score / (len(faceplusplus_res[:-1]) + int(faceplusplus_res[-1][0])) * 100),
        "ethnicity_score_unfailed": '%1.2f' % (ethnicity_score / len(faceplusplus_res[:-1]) * 100),
        "ethnicity_score_with_fails": '%1.2f' % (ethnicity_score / (len(faceplusplus_res[:-1]) + int(faceplusplus_res[-1][0])) * 100),
        "age_score": '%1.2f' % age_score
    }
    

if __name__ == '__main__':
    action = sys.argv[1]
    if action == "store":
        store_dataframe()
    elif action == "test":
        test_faceplusplus()
    elif action == "score":
        print (score_faceplusplus())
        print(score_slightcorp())

