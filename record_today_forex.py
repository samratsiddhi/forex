import psycopg2 as ps
import requests
from datetime import date,timedelta
import time

# establish connection to db
try:  
    conn = ps.connect('host=127.0.0.1  \
                      dbname= forex \
                      user = postgres  \
                      password = 1234'
                      )
    conn.set_session(autocommit=True)
    print('connection established sucessfully')
except ps.Error as e:
    print (e)

# create a cursor
try:  
    cur = conn.cursor()
    print('cursor created sucessfully')
except ps.Error as e:
    print (e)


# use api to get current forexdata
response = requests.get("https://api.fastforex.io/fetch-all?api_key=97e3e44c3e-440a6dbec3-rvha83")
rates = response.json()['results']

# insert current forex data into the database
today = date.today()
sql = "delete from forexhistory where recordDate='" + str(today) +"';"
cur.execute(sql)
for country, rate in rates.items():
    cur.execute("truncate table currentforex")
    cur.execute("insert into currentforex(countryCode,rate,recordDate)values(%s,%s,%s)",(country,rate,today))
    print("inserting into currentforex")

    cur.execute("insert into forexhistory(countryCode,rate,recordDate)values(%s,%s,%s)",(country,rate,today))
    print("inserting todays data into forexhistory")

conn.close()