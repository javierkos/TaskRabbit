import requests
import json
import time

class ImageTestService:
    def __init__(self, service, X):
        service_endpoints = {
            "slightcorp_face": "https://face-api.sightcorp.com/",
        }

        self.service, self.service_endpoint = service, service_endpoints[service]
        self.X = X

    def get_error(self):
        #lol
        print ("")


    def get_accuracy(self, y, pred):
        return sum([1 if val == pred[i] else 0 for i,val in enumerate(y)])/len(y)

    def get_slightcorp_adjusted_ethnicity(self, ethnic_data):
        dct = {
            "african": "black",
            "asian": "asian",
            "caucasian": "white",
            "hispanic": "other"
        }
        
        return dct[sorted(ethnic_data.items(), key=lambda x: x[1])[-1][0]]

    
    def test_slightcorp(self):
        results = []
        fails = 0
        i = 0
        for index, row in self.X.iterrows():
            if i % 25 == 0:
                print (i)
            json_resp = requests.post('https://api-face.sightcorp.com/api/detect/',
                                      data={'app_key': 'df749b63256e45e39059faa0c4f6887a', 'ethnicity': True},
                                      files={'img': ('filename', open('test_datasets/UTKFace/' + row["f_name"], 'rb'))})

            json_obj = json.loads(json_resp.text)

            if 'people' in list(json_obj.keys()) and len(json_obj["people"]):
                results.append({
                    "actual_age": row["age"],
                    "predicted_age": json_obj["people"][0]["age"],
                    "actual_ethnicity": row["race"],
                    "predicted_ethnicity": self.get_slightcorp_adjusted_ethnicity(json_obj["people"][0]["ethnicity"]),
                    "actual_gender": row["gender"],
                    "predicted_gender": json_obj["people"][0]["gender"],
                    "mood": json_obj["people"][0]["mood"]
                })
            else:
                fails += 1
            time.sleep(1)
            i += 1
        results.append([fails])
        with open("results/slightcorp.json", "w") as write_file:
            json.dump(results, write_file)




