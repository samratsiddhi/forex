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


# create table history forex 
try:
    cur.execute('drop table if exists forexhistory')

    cur.execute("""
                create table forexhistory(
                    id serial primary key ,
                    countryCode varchar(3),
                    rate float,
                    recordDate date
                );
                """)
    print('table forexhistory created')
except ps.Error as e:
    print (e)


# create table current forex 
try:
    cur.execute('drop table if exists currentforex')

    cur.execute("""
                    create table currentforex(
                        id serial primary key ,
                        countryCode varchar(3),
                        rate float,
                        recordDate date
                    );
                """)
    print('table currentforex created')
except ps.Error as e:
    print (e)


# create tablecountry codes
try:
    cur.execute('drop table if exists country_codes')
    cur.execute("""
                    create table country_codes(
                        id serial primary key ,
                        countryCode varchar(3),
                        countryName varchar(50)
                    );
                """)
    print('table country_codes created')
except ps.Error as e:
    print (e)


# use api to get county name and country code
currencies = requests.get("https://api.fastforex.io/currencies?api_key=97e3e44c3e-440a6dbec3-rvha83")
codes =currencies.json()['currencies']

# insert country and their codes into the database
for code,country in codes.items():
    cur.execute("insert into country_codes(countryCode,countryName)values(%s,%s)",(code,country))
    print("inserted into country_codes")

# insert history data into table 
cur.execute("""select countrycode from country_codes;""")
codes = cur.fetchall()

for code in codes:
    date = date.today() 
    d = date - timedelta(days=2)
    while d <= date:
        url = "https://api.fastforex.io/historical?api_key=97e3e44c3e-440a6dbec3-rvha83&date="+str(d)+"&to="+ code[0]
        time.sleep(0.01)
        history = requests.get(url)
        time.sleep(0.01)
        d = d + timedelta(days=1)
        if(history.status_code == 200):
            rates = history.json()['results']
            for x, y in rates.items():
                countrycode = x
                forexrate = y
                
            cur.execute("""
                        insert into forexhistory(countryCode,rate,recordDate)
                        values(%s,%s,%s)
                        """,
                       (countrycode,forexrate,history.json()['date'])
                       )
            time.sleep(0.01)
            print("inserting " + countrycode+ "  " + str(forexrate) + "date:" + str(history.json()['date']))
            print("inserted into all history data into forexhistory")

# close connection
conn.close()