# login_with_db
from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

conn = sqlite3.connect('database.db')
print("Opened database successfully")
conn.execute('CREATE TABLE IF NOT EXISTS shopping (item TEXT, num TEXT, price TEXT)')
print("Table created successfully")
conn.close()

app = Flask(__name__)

# session 을 설정 안하면 에러가 난다.
app.secret_key = b'1234abc'

con = sqlite3.connect("join_info.db")

# Connection 으로부터 Cursor 생성
cur = con.cursor()
# SQL 쿼리 실행
# CREATE TABLE 테이블명(변수명 변수 자료형, )
try:
    cur.execute("CREATE TABLE info(ID  text PRIMARY KEY , PW text, MONEY text)")
    con.commit()
# Connection 닫기
    con.close()
except:
    print("already.db")

@app.route('/')
def welcome():
    return "welcome"

@app.route("/sign_up", methods=['POST'])
def sign_up():
    if request.method == 'POST':
        # Compare with
        con = sqlite3.connect("join_info.db")
        cur = con.cursor()

        want_id = request.form.get('want_id', "not data")
        want_pwd = request.form.get('want_pwd', "not data")

        if want_id == "not data":
            return render_template('join.html')
        # make execute
        try:
            execute = "INSERT INTO info(ID, PW, MONEY) VALUES (?, ?, 10000)"
            cur.execute(execute, (want_id, want_pwd))
            print("Success Join")
            con.commit()
            con.close()
            return redirect(url_for('login'))
        except:
            print("Fail Join")
            return render_template('join.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    global id_info
    if not session.get('logged_in'):
        if request.method == 'POST':

            con = sqlite3.connect("join_info.db")
            cur = con.cursor()

            login_id = request.form.get('id', "not data")
            login_pwd = request.form.get('pwd', "not data")

            if login_id == "not data":
                return render_template('login.html')

            # make execute
            execute = "SELECT * FROM info where id =(?)"
            cur.execute(execute, [login_id])
            rows = cur.fetchall()
            con.commit()
            con.close()

            try:
                if rows[0][1] == login_pwd:
                    print("Success Login")
                    session['logged_in'] = True
                    id_info = login_id
                    return redirect(url_for('addrec'))
            except:
                print("Fail Login")
                return render_template('login.html')
    else:
        return redirect(url_for('addrec'))

    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('welcome'))

#연습 - 장보기 목록 만들기
@app.route('/shopping', methods=['POST','GET'])
def shopping():

    if request.method == 'POST':
        # 데이터베이스에서 데이터를 가져 온다.
        con = sqlite3.connect("database.db")
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("select * from shopping")
        rows = cur.fetchall()
        print("DB:")
        print(rows)
        return render_template('shopping.html', rows=rows)
    else:
        # 데이터베이스에서 데이터를 가져 온다.
        con = sqlite3.connect("database.db")
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("select * from shopping")
        rows = cur.fetchall()
        print("DB:")
        print(rows)
        return render_template('shopping.html', rows=rows)

@app.route('/addrec', methods = ['POST','GET'])
def addrec():
    msg = ""
    if request.method == 'POST':
        try:
            item = request.form['item']
            num = request.form['num']
            price = request.form['price']

            with sqlite3.connect("database.db") as con:
                cur = con.cursor()
                cur.execute("INSERT INTO shopping (item, num, price) VALUES (?, ?, ?)", (item, num, price))
                con.commit()
                msg = "Record successfully added"
                return render_template("shopping_add_result.html", message=msg)
        except:
            con.rollback()
            msg = "Error in insert operation"
            return render_template("shopping_add_result.html", message=msg)
    else:
        return render_template("shopping_add_result.html", message=msg)

@app.route('/buy', methods = ['POST'])
def buy():
    global id_info
    if request.method == 'POST':
        con = sqlite3.connect('join_info.db')
        cur = con.cursor()

        # make execute"
        execute = "SELECT * FROM info"
        cur.execute(execute)
        rows = cur.fetchall()

        print("id_info", id_info)

        for id, pwd, money in rows:
            if id == id_info:
                print("id pwd money", id, pwd, money)

        con = sqlite3.connect("database.db")
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("SELECT * FROM shopping")
        rows = cur.fetchall()
        total = 0

        for row in rows:
            print("row item", row['item'])
            print("row num", row['num'])
            print("row price", row['price'])
            total = total + int(row['price'])

        money = int(money)

        if money >= total:
            print("you've successfully got the item(s)")
            print(money - total)
            return redirect(url_for('addrec'))

if __name__ == '__main__':
    app.run()
