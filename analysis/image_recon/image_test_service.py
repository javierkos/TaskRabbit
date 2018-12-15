import requests
import json

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
    
    def test_slightcorp(self):
        results = []
        fails = 0
        for index, row in self.X.iterrows():
            print (row)
            json_resp = requests.post('https://api-face.sightcorp.com/api/detect/',
                                      data={'app_key': 'df749b63256e45e39059faa0c4f6887a', 'ethnicity': True},
                                      files={'img': ('filename', open('test_datasets/UTKFace/' + row["f_name"], 'rb'))})

            json_obj = json.loads(json_resp.text)
            print (json_obj)
            print(list(json_obj.keys()))
            if 'people' in list(json_obj.keys()) and len(json_obj["people"]):
                results.append({
                    "actual_age": row["age"],
                    "predicted_age": json_obj["people"][0]
                })
                print (json_obj['people'])
            else:
                fails += 1



