from analysis.image_recon.face_plusplus.face_plusplus import *
import sqlite3
import pandas as pd

conn = sqlite3.connect("../../databases/taskrabbit_los_angeles.db")
c = conn.cursor()

c.execute("SELECT tasker_id, picture FROM taskers")
df_dict = {"tasker_id": [], "url": []}
for row in c.fetchall():
    df_dict["tasker_id"].append(row[0])
    df_dict["url"].append(row[1])

X = pd.DataFrame(df_dict)

call_facedetect(X, conn)
