from flask import Flask
from flask import Flask, flash, redirect, render_template, request, session, abort
import os
from os import popen
import sqlite3


conn = sqlite3.connect("users.db")
cursor = conn.cursor()


cursor.execute("""CREATE TABLE IF NOT EXISTS users
                  (id, username, password)
               """)

users = [('1', 'admin', 'verystrongpassword'),
          ('2', 'notadmin', 'amanotadmin'),
          ('3', 'user', 'amajustauser')]

cursor.executemany("INSERT INTO users VALUES (?,?,?)", users)
conn.commit()

app = Flask(__name__)
app.secret_key = os.urandom(12)

def rp(command):
    return popen(command).read()

@app.route('/')
def home():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return redirect("/lookup")

@app.route('/lookup', methods = ['POST', 'GET'])
def lookup():
    if not session.get('logged_in'):
        return redirect("/")
    address = None
    if request.method == 'POST':
        address = request.form['address']
    return """
    <html>
        <body>""" + "Result:\n<br>\n" + (rp("nslookup " + address).replace('\n', '\n<br>')  if address else "") + """
        <style>
        body {
        font-family: Arial;
        background-image: url("https://lescinskas.lt/assets/img/posts/2019/docker.png");
        min-height: 380px;
        background-position: center;
        background-repeat: no-repeat;
        background-size: cover;
        position: relative;
        }
        </style>
          <form action = "/lookup" method = "POST">
             <p><h3>Enter address to lookup</h3></p>
             <p><input type = 'text' name = 'address'/></p>
             <p><input type = 'submit' value = 'Lookup'/></p>
          </form>
       </body>
    </html>
    """

@app.route('/login', methods=['POST'])
def do_admin_login():

    username = request.form['username']
    password = request.form['password']
    sql = "SELECT id FROM users WHERE username = '"+str(username)+"' AND password = '"+str(password)+"'"
    id = str(cursor.execute(sql).fetchall())
    id = id.replace(')','')
    id = id.replace('(','')
    id = id.replace(']','')
    id = id.replace('[','')
    id = id.replace(',','')
    id = id.replace("'","")
    id = id.replace(' ','')

    if id.isdigit():
        session['logged_in'] = True
    else:
        flash('wrong password!')
    return home()

@app.route("/logout")
def logout():
    session['logged_in'] = False
    return home()

if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(host='127.0.0.1', port=1488)