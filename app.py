
from flask import *
import sqlite3

app = Flask(__name__, static_folder='static')

con = sqlite3.connect('database.db')
con.execute('''
    CREATE TABLE IF NOT EXISTS LOGIN(
    U_NAME VARCHAR2(10) PRIMARY KEY,
    PWD VARCHAR2(10) NOT NULL,
    DPLOC VARCHAR2(50) NOT NULL);
''')
# con.execute("INSERT IF NOT EXISTS INTO LOGIN IF NOT EXISTS (U_NAME,PWD,DPLOC) VALUES('{u}','{p}','images/img1.jpeg');".format(u="admin", p="admin"))
con.commit
con.close()
@app.route('/')
@app.route('/home')
def home_page():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')
@app.route('/login')

def login():
    return render_template('login.html')

@app.route('/login/',methods=['POST'])
def logged_in():
    con = sqlite3.connect("database.db")
    U_NAME = request.form["uname"]
    print(U_NAME+"----------------------")
    PWD = request.form["pwd"]
    cur = con.cursor()
    cur.execute("SELECT U_NAME,PWD,DPLOC FROM LOGIN WHERE U_NAME='{un}' AND PWD='{pw}';".format(
        un=U_NAME, pw= PWD))
    acc = cur.fetchall()
    if len(acc) == 1:
        return render_template('menu.html')
    else:
        return render_template('menu.html')

@app.route('/menu')
def menu():
    return render_template('menu.html')


app.run(debug=True)
