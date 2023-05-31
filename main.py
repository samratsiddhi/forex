from flask import Flask,url_for,request,render_template
import psycopg2 as ps
import requests
from datetime import date
import matplotlib.pyplot as plt
import pandas as pd

app = Flask(__name__)
app.secret_key = "12345"

# function to create line chart of choosen currncy history
def create_line_graph(table):
    df_data = pd.DataFrame(table,columns=['code','rate','date','country'])
    x_axis = df_data['date'].astype(str)
    y_axis = df_data['rate'].tolist()
    fig, ax = plt.subplots()
    ax.plot(x_axis, y_axis)
    ax.set_xlabel('Time')
    ax.set_ylabel('Rate compared with USD')
    plt.xticks(rotation=20)
    fig.savefig('static/images/history.png')  

@app.route("/")
def home():
    # connecting  to database
    conn = connect_to_db()
    if conn==0:
        return "failed to connect to database"
    else:
        # use api to get current forexdata
        response = requests.get("https://api.fastforex.io/fetch-all?api_key=97e3e44c3e-440a6dbec3-rvha83")
        rates = response.json()['results']

        cur = conn.cursor()
       
        # retriving data from database 
        cur.execute("""
                select cc.countrycode,
                        cc.countryname,
                        cf.rate 
                from currentforex cf
                join country_codes cc
                on cc.countrycode =cf.countrycode;
                    """)
        result = cur.fetchall()
        conn.close()

        return render_template("index.html", table_data=result)

           
@app.route("/convert",methods = ['GET', 'POST'])
def convert():
    # connecting to database
    conn = connect_to_db()
    if conn==0:
        return "failed to connect to database"
    else:
        # retriving country and their country code data from database
        cur = conn.cursor()
        cur.execute("""
                select countrycode,
                        countryname 
                from country_codes;
                    """) 
        result = cur.fetchall()
        conn.close()
    if request.method == "POST":
        info = {
            'from' : request.form['from'].upper(),
            'to' : request.form['to'],
            'amount' : request.form['amount']
        }
        converted_amount = convert(info['from'],info['to'],info['amount'])
        return render_template("convert_currency.html", form_data=result, conversion=converted_amount)
    else:
        return render_template("convert_currency.html",form_data=result)
    

@app.route("/history",methods = ['GET', 'POST'])
def history():
    # connecting to database
    conn = connect_to_db()
    if conn==0:
        return "failed to connect to database"
    else:
        # retriving country and their country code data from database
        cur = conn.cursor()
        cur.execute("""
                select countrycode,
                        countryname 
                from country_codes;
                    """) 
        result = cur.fetchall()
        conn.close()
    if request.method == "POST":
        country = request.form['country']
        conn = connect_to_db()
        if conn==0:
            return "failed to connect to database"
        else:
            # retriving country and their country code data from database
            cur = conn.cursor()
            sql = "select f.countrycode ,f.rate,f.recorddate,c.countryname from forexhistory f join country_codes c \
                on c.countrycode = f.countrycode where c.countryCode='"+ country +"';"
            cur.execute(sql)
            table = cur.fetchall() 
            create_line_graph(table)
            return render_template("get_history.html",form_data=result,table_data=table)       
    else:
        return render_template("get_history.html",form_data=result)

# function to connect to databse
def connect_to_db():
    try:
        conn = ps.connect('host=127.0.0.1  \
                      dbname= forex \
                      user = postgres  \
                      password = 1234'
                      )
        conn.set_session(autocommit=True)
        return conn
    except ps.Error as e:
        return 0


# function to convert currency
def convert(convert_from,convert_to,amount):
    url = "https://api.fastforex.io/convert?api_key=97e3e44c3e-440a6dbec3-rvha83&from="+convert_from+"&to="+convert_to+"&amount="+str(amount)
    convert = requests.get(url)
    return convert.json()['result'][convert_to]

if __name__ == "__main__":
    app.run(debug= True)

