from flask import Flask, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)
app.secret_key = "Pavan@2007"

# Database connection
def get_db():
    return sqlite3.connect("crm.db")

# Initialize DB
@app.route('/init_db')
def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            phone TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            password TEXT
        )
    ''')

    conn.commit()
    conn.close()
    return "Database initialized"

# Create admin user
@app.route('/create_user')
def create_user():
    conn = get_db()
    cursor = conn.cursor()

    username = "admin"
    password = generate_password_hash("1234")

    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                   (username, password))

    conn.commit()
    conn.close()
    return "User created"

# Home page
@app.route('/', methods=['GET'])
def index():
    if 'user' not in session:
        return redirect('/login')

    conn = get_db()
    cursor = conn.cursor()

    search = request.args.get('search')

    if search:
        cursor.execute(
            "SELECT * FROM customers WHERE name LIKE ? OR email LIKE ?",
            ('%' + search + '%', '%' + search + '%')
        )
    else:
        cursor.execute("SELECT * FROM customers")

    data = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) FROM customers")
    total = cursor.fetchone()[0]

    conn.close()

    return render_template('index.html', customers=data, total=total)

# Add customer
@app.route('/add', methods=['GET', 'POST'])
def add():
    if 'user' not in session:
        return redirect('/login')

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO customers (name, email, phone) VALUES (?, ?, ?)",
            (name, email, phone)
        )

        conn.commit()
        conn.close()

        return redirect('/')

    return render_template('add.html')

# Delete
@app.route('/delete/<int:id>')
def delete(id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM customers WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect('/')

# Edit
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    conn = get_db()
    cursor = conn.cursor()

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']

        cursor.execute(
            "UPDATE customers SET name=?, email=?, phone=? WHERE id=?",
            (name, email, phone, id)
        )

        conn.commit()
        conn.close()

        return redirect('/')

    cursor.execute("SELECT * FROM customers WHERE id=?", (id,))
    data = cursor.fetchone()
    conn.close()

    return render_template('edit.html', customer=data)

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        user = cursor.fetchone()

        conn.close()

        if user and check_password_hash(user[2], password):
            session['user'] = username
            return redirect('/')
        else:
            return render_template('login.html', error="Invalid Credentials")

    return render_template('login.html')

# Logout
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')

import os

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)