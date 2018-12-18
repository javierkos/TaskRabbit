import requests
import analysis.image_recon.constants as const
import json
import sqlite3

def api_call(ret_attributes, image_url):
    return requests.post(const.FACE_PLUSPLUS_ENDPOINT,
                         {'api_key': const.FACE_PLUSPLUS_KEY,
                          'api_secret': const.FACE_PLUSPLUS_SECRET,
                          'return_attributes': ret_attributes,
                          'image_url': image_url})

def call_facedetect(X, conn):
    c = conn.cursor()
    fails, i = 0, 0
    for index, row in X.iterrows():
        if i % 25 == 0:
            print(i)
        json_obj = json.loads(api_call("gender,age,smiling,ethnicity", row["url"]).text)
            
        if 'faces' in list(json_obj.keys()):
            try:
                insert_data = (
                    row["tasker_id"],
                    json_obj["faces"][0]["attributes"]["age"]["value"],
                    json_obj["faces"][0]["attributes"]["smile"]["value"],
                    json_obj["faces"][0]["attributes"]["ethnicity"]["value"],
                    json_obj["faces"][0]["attributes"]["gender"]["value"]
                )
                '''
                results.append({
                    "tasker_id": row["tasker_id"],
                    "predicted_age": json_obj["faces"][0]["attributes"]["age"]["value"],
                    "predicted_ethnicity": json_obj["faces"][0]["attributes"]["ethnicity"]["value"],
                    "predicted_gender": json_obj["faces"][0]["attributes"]["gender"]["value"],
                    "mood": json_obj["faces"][0]["attributes"]["smile"]["value"]
                })
                '''
                c.execute("INSERT INTO tasker_img_predictions VALUES (?,?,?,?,?)", insert_data)
                conn.commit()
            except Exception as e:
                fails += 1
        else:
            fails += 1
        i += 1
    print (fails)