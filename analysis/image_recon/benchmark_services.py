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

def test_dataframe():
    with open("test_datasets/UTK_df.pkl", "rb") as df_file:
        X = pickle.load(df_file)
    its = ImageTestService("slightcorp_face", X.sample(250))
    its.test_slightcorp()

def get_slightcorp_genre(genre_score):
    return "1" if genre_score > 0 else "0"

def get_slightcorp_ethnicity(ethnicity):
    dct = {
        "white": ["0"],
        "black": ["1"],
        "asian": ["2"],
        "other": ["3", "4"]
    }
    return dct[ethnicity]

def score_slightcorp():
    with open("results/slightcorp.json", "r") as read_file:
        slightcorp_res = json.load(read_file)
    gender_score = sum([1 if person["actual_genre"] == get_slightcorp_genre(int(person["predicted_genre"]))
                        else 0 for person in slightcorp_res[:-1]])

    ethnicity_score = sum([1 if person["actual_ethnicity"] in get_slightcorp_ethnicity(person["predicted_ethnicity"])
                        else 0 for person in slightcorp_res[:-1]])

    return {
        "gender_score_unfailed": '%1.2f' % (gender_score / len(slightcorp_res[:-1]) * 100),
        "gender_scoe_with_fails": '%1.2f' % (gender_score / (len(slightcorp_res[:-1]) + int(slightcorp_res[-1][0])) * 100),
        "ethnicity_score_unfailed": '%1.2f' % (ethnicity_score / len(slightcorp_res[:-1]) * 100),
        "ethnicity_score_with_fails": '%1.2f' % (ethnicity_score / (len(slightcorp_res[:-1]) + int(slightcorp_res[-1][0])) * 100),
    }
    

if __name__ == '__main__':
    action = sys.argv[1]
    if action == "store":
        store_dataframe()
    elif action == "test":
        test_dataframe()
    elif action == "score":
        score_slightcorp()

