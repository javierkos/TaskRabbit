import pandas as pd
import os
import pickle
import sys
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
    its = ImageTestService("slightcorp_face", X.tail(2))
    its.test_slightcorp()

if __name__ == '__main__':
    action = sys.argv[1]
    if action == "store":
        store_dataframe()
    elif action == "test":
        test_dataframe()

