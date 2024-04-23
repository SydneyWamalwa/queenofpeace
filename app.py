from flask import Flask, render_template, request, jsonify
from flask_session import Session
from flask_bcrypt import Bcrypt
from urllib.parse import quote
import sqlite3
import os

app = Flask(__name__)
secret_key = os.urandom(24)
app.secret_key = secret_key
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)
bcrypt = Bcrypt(app)

try:
    with sqlite3.connect('queenofpeace.db') as connection:
        cursor = connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS donations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                amount REAL NOT NULL,
                payment_reference TEXT NOT NULL

            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                comment TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS subscribers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL
            )
        ''')
    connection.commit()
except Exception as e:
    print(f"Error connecting to the database: {e}")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/donate', methods=['POST', 'GET'])
def donate():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        amount = request.form['amount']

        with sqlite3.connect('queenofpeace.db') as connection:
            cursor = connection.cursor()
            cursor.execute("INSERT INTO donations (name, email, amount) VALUES (?, ?, ?)",
                           (name, email, amount))
            connection.commit()

        return render_template('donate.html', success=True)
    else:
        return render_template('donate.html', success=False)

@app.route('/post_comment', methods=['POST'])
def post_comment():
    if request.method == 'POST':
        name = request.form['name']
        comment = request.form['comment']

        with sqlite3.connect('queenofpeace.db') as connection:
            cursor = connection.cursor()
            cursor.execute("INSERT INTO comments (name, comment) VALUES (?, ?)",
                           (name, comment))
            connection.commit()

        return render_template('comments.html')
    else:
        return jsonify({"status": "error"})

@app.route('/get_comments')
def get_comments():
    try:
        with sqlite3.connect('queenofpeace.db') as connection:
            cursor = connection.cursor()
            cursor.execute('SELECT name, comment FROM comments')
            comments = cursor.fetchall()

        # Transform the comments into a list of dictionaries
        comments_data = [{"name": comment[0], "comment": comment[1]} for comment in comments]

        return jsonify(comments_data)

    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/store_data', methods=['POST'])
def store_data():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        amount = request.form['amount']
        payment_reference = request.form['payment_reference']

        try:
            with sqlite3.connect('queenofpeace.db') as connection:
                cursor = connection.cursor()
                cursor.execute("INSERT INTO donations (name, email, amount, payment_reference) VALUES (?, ?, ?, ?)",
                               (name, email, amount, payment_reference))
                connection.commit()

            return jsonify({"status": "success"})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})

    return jsonify({"status": "error", "message": "Invalid request method"})

@app.route('/subscribe', methods=['POST'])
def subscribe():
    if request.method == 'POST':
        email = request.form['subscribe-email']
        try:
            with sqlite3.connect('queenofpeace.db') as connection:
                cursor = connection.cursor()
                cursor.execute("INSERT INTO subscribers(email) VALUES (?)", (email,))
                connection.commit()
                return jsonify({"status": "success"})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})
    return jsonify({"status": "error", "message": "Invalid request method"})

@app.route('/conflict.html')
def conflict():
    return render_template('conflict.html')

@app.route('/empowernment.html')
def empowernment():
    return render_template('empowernment.html')

@app.route('/governance.html')
def governancet():
    return render_template('governance.html')

@app.route('/rights.html')
def rights():
    return render_template('rights.html')


if __name__ == '__main__':
    app.run(host="0.0.0.0",port=5000)
