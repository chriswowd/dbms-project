from flask import *
import sqlite3
import pdfkit


app = Flask(__name__, static_folder='static')


con = sqlite3.connect('database.db')
con.execute('''
    CREATE TABLE IF NOT EXISTS LOGIN(
    U_NAME VARCHAR2(10) PRIMARY KEY,
    PWD VARCHAR2(10) NOT NULL,
    DPLOC VARCHAR2(50) NOT NULL);
''')
con.execute('''
    CREATE TABLE IF NOT EXISTS PRODUCT(
    PROD_ID VARCHAR(10) PRIMARY KEY,
    NAME VARCHAR(50) NOT NULL,
    BRAND VARCHAR(50) ,
    PIC_LOC VARCHAR2(50) NOT NULL,
    PRICE NUMBER(10,2));
''')
con.execute('''
    CREATE TABLE IF NOT EXISTS SIZES(
    PROD_ID VARCHAR,
    SIZE INTEGER,
    AVI INTEGER);
''')
con.execute('''
    CREATE TABLE IF NOT EXISTS CART(
    SRNO INTEGER PRIMARY KEY AUTOINCREMENT,
    PROD_ID VARCHAR,
    NAME VARCHAR(50) NOT NULL,
    PIC_LOC VARCHAR2(50) NOT NULL,
    PRICE NUMBER(10,2),
    SIZE INTEGER);
''')

con.execute('''
    CREATE TABLE IF NOT EXISTS PURCHASED(
    BILL_ID INTEGER,
    PROD_ID VARCHAR,
    NAME VARCHAR(50) NOT NULL,
    PIC_LOC VARCHAR2(50) NOT NULL,
    PRICE NUMBER(10,2),
    SIZE INTEGER);
''')
con.execute('''
    CREATE TABLE IF NOT EXISTS CUSTOMER(
    BILL_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    FNAME VARCHAR(20) NOT NULL,
    LNAME VARCHAR(50) NOT NULL,
    PHONE INTEGER NOT NULL,
    EMAIL VARCHAR(20),
    ADDRESS VARCHAR(50) NOT NULL,
    BILL_TOTAL NUMBER(10,2)  );    
''')
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


@app.route('/delete/<int:id>')
def delete(id):
    con = sqlite3.connect("database.db")
    cur=con.cursor()
    cur.execute("DELETE FROM CART WHERE SRNO={i};".format(i=id))
    con.commit()
    cur.execute("SELECT * FROM PRODUCT")
    data=cur.fetchall()
    cur.execute("SELECT * FROM SIZES")
    size_data=cur.fetchall()
    cur.execute("SELECT * FROM CART")
    cart=cur.fetchall()
    con.commit()
    return render_template('menu.html',cart=cart,data=data,size_data=size_data)
    

@app.route('/login/',methods=['POST'])
def logged_in():
    con = sqlite3.connect("database.db")
    uname = request.form["uname"]
    pwd = request.form["pwd"]
    cur = con.cursor()
    cur.execute("SELECT U_NAME,PWD FROM LOGIN WHERE U_NAME='{un}' AND PWD='{pw}';".format(un=uname, pw=pwd))
    acc = cur.fetchall()
    if len(acc) == 1:
        con = sqlite3.connect("database.db")
        cur = con.cursor()
        cur.execute("SELECT * FROM PRODUCT")
        data=cur.fetchall()
        cur.execute("SELECT * FROM SIZES")
        size_data=cur.fetchall()
        cur.execute("SELECT * FROM CART")
        cart=cur.fetchall()
        return render_template('menu.html',data=data,size_data=size_data,cart=cart)
    else:
        return render_template('error.html')


@app.route('/menu',methods=['GET', 'POST'])
def menu():
    con = sqlite3.connect("database.db")
    cur=con.cursor()
    shoe= request.form.get("shoe")
    if shoe != None:
        l=shoe.split(",")    
        prod_id=l[0]
        size=l[1]
        cur.execute("SELECT PIC_LOC,NAME,PRICE FROM PRODUCT WHERE PROD_ID='{p}';".format(p=prod_id))
        data=cur.fetchall()
        for i in data:
            pic=i[0]
            name=i[1]
            price=i[2]
        cur.execute(f'''INSERT INTO CART (PROD_ID,PIC_LOC,NAME,PRICE,SIZE) VALUES ("{prod_id}","{pic}",'{name}',"{price}",'{size}');''')
        cur.execute("SELECT * FROM PRODUCT")
        data=cur.fetchall()
        cur.execute("SELECT * FROM SIZES")
        size_data=cur.fetchall()
        cur.execute("SELECT * FROM CART")
        cart=cur.fetchall()
        con.commit()
      
        return render_template('menu.html',cart=cart,data=data,size_data=size_data)
    
    cur.execute("SELECT * FROM PRODUCT")
    data=cur.fetchall()
    cur.execute("SELECT * FROM SIZES")
    size_data=cur.fetchall()
    cur.execute("SELECT * FROM CART")
    cart=cur.fetchall()
    con.commit()
    return render_template('menu.html',cart=cart,data=data,size_data=size_data)


@app.route('/customer')
def customer():
    
    con = sqlite3.connect("database.db")
    cur=con.cursor()   
    cur.execute("SELECT * FROM CART")
    cart=cur.fetchall()
    con.commit()
    tcost=0
    totalitem=0
    for i in cart:
        tcost=tcost+i[4]
        totalitem=totalitem+1
    return render_template('customer.html',cart=cart,tcost=tcost,totalitem=totalitem)

@app.route('/thank',methods=[ 'POST'])
def thank():
    first=request.form.get("first")
    last=request.form.get("last")
    phno=request.form.get("phno")
    email=request.form.get("email")
    address=request.form.get("address")
    con = sqlite3.connect("database.db")
    cur=con.cursor()
    cur.execute("SELECT * FROM CART")
    cart=cur.fetchall()
    con.commit()
    tcost=0
    totalitem=0
    for i in cart:
        tcost=tcost+i[4]
        totalitem=totalitem+1
    cur.execute(f'''INSERT INTO CUSTOMER (FNAME,LNAME,PHONE,EMAIL,ADDRESS,BILL_TOTAL) VALUES ("{first}","{last}","{phno}","{email}","{address}","{tcost}");''')
    con.commit()
    cur.execute("SELECT * FROM CART")
    cart=cur.fetchall()
    cur.execute("SELECT MAX(BILL_ID) FROM CUSTOMER;")

    bill_id=cur.fetchall()
    for i in bill_id:
        bid=i[0]
    for item in cart:
        cur.execute(f'''INSERT INTO PURCHASED (BILL_ID,PROD_ID,PIC_LOC,NAME,PRICE,SIZE) VALUES ("{bid}","{item[1]}","{item[3]}",'{item[2]}',"{item[4]}",'{item[5]}');''')
        con.commit()
    cur.execute("DELETE FROM CART")
    con.commit()
    con.close()
    return render_template("thank.html",bid=bid)

@app.route('/bill')
def bill():
    con = sqlite3.connect("database.db")
    cur=con.cursor()
    cur.execute("SELECT MAX(BILL_ID) FROM CUSTOMER;")
    bill_id=cur.fetchall()
    for i in bill_id:
        bid=i[0]
    cur.execute("SELECT * FROM PURCHASED WHERE BILL_ID={i};".format(i=bid))
    cart=cur.fetchall()
    con.commit()
    cur.execute("SELECT * FROM CUSTOMER WHERE BILL_ID={i};".format(i=bid))
    cust=cur.fetchall()
    tcost=0
    totalitem=0
    for i in cart:
        tcost=tcost+i[4]
        totalitem=totalitem+1 
    rendered = render_template('bill.html',cart=cart,cust=cust,tcost=tcost,totalitem=totalitem)
    config = pdfkit.configuration(
    wkhtmltopdf="C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe")
    pdf = pdfkit.from_string(rendered, configuration=config)

    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=bill.pdf'

    return response
app.run(debug=True)
