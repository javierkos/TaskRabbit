import sqlite3

conn = sqlite3.connect('databases/taskrabbit_ny.db')
c = conn.cursor()

with open("ny_n.txt") as f:
    content = f.readlines()

for line in content:
    postcode = line
    c.execute("INSERT INTO locations(name,city_id) VALUES('" + postcode + "',1)")
conn.commit()
c.close()