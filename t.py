import sqlite3


conn = sqlite3.connect("databases/taskrabbit_los_angeles.db")
conn2 = sqlite3.connect("/Users/javierpascual/Downloads/TaskRabbit/databases/taskrabbit_los_angeles.db")

c = conn.cursor()
c2 = conn2.cursor()

c2.execute("SELECT text, service_id, tasker_id FROM descriptions")
print ("xd")
for row in c2.fetchall():
    print (row)
    c.execute("INSERT INTO descriptions(text,service_id,tasker_id) VALUES(?,?,?)", row)

conn.commit()