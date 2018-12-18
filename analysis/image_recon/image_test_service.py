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
        fails, i = 0, 0
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

    def test_faceplusplus(self):
        results = []
        fails = 0
        i = 0
        for index, row in self.X.iterrows():
            if i % 25 == 0:
                print (i)
            json_resp = requests.post('https://api-us.faceplusplus.com/facepp/v3/detect',
                                      data={'api_key': 'p2Xus5m7q7pDON-gris92aU-T14Mqyfs',
                                            'api_secret': "CnQzPyBY5yKJkkHeEEl4Si-2KNzx7yf0",
                                            'return_attributes': "gender,age,smiling,ethnicity"},
                                      files={'image_file': ('filename', open('test_datasets/UTKFace/' + row["f_name"], 'rb'))})
            json_obj = json.loads(json_resp.text)

            if 'faces' in list(json_obj.keys()):
                try:
                    results.append({
                        "actual_age": row["age"],
                        "predicted_age": json_obj["faces"][0]["attributes"]["age"]["value"],
                        "actual_ethnicity": row["race"],
                        "predicted_ethnicity": json_obj["faces"][0]["attributes"]["ethnicity"]["value"],
                        "actual_gender": row["gender"],
                        "predicted_gender": json_obj["faces"][0]["attributes"]["gender"]["value"],
                        "mood": json_obj["faces"][0]["attributes"]["smile"]["value"]
                    })
                except Exception:
                    fails += 1
            else:
                fails += 1
            i += 1
        results.append([fails])
        with open("results/faceplusplus.json", "w") as write_file:
            json.dump(results, write_file)






