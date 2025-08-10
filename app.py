from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

def get_db_connection():
    conn = sqlite3.connect('LoginData.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        fname = request.form['first_name'].strip()
        lname = request.form['last_name'].strip()
        email = request.form['email'].strip().lower()
        password = request.form['password'].strip()
        role = request.form['role']

        if not fname or not lname or not email or not password:
            flash('Please fill in all fields.', 'error')
            return redirect(url_for('signup'))

        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO USERS (first_name, last_name, email, password, role) VALUES (?, ?, ?, ?, ?)',
                         (fname, lname, email, password, role))
            conn.commit()
            flash('Account created! You can now login.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Email already registered. Please login or use another email.', 'error')
            return redirect(url_for('signup'))
        finally:
            conn.close()

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        password = request.form['password'].strip()
        role = request.form['role']

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM USERS WHERE email = ? AND password = ? AND role = ?',
                            (email, password, role)).fetchone()
        conn.close()

        if user:
            session['user'] = dict(user)
            session['role'] = role
            if role == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('user_dashboard'))
        else:
            flash('Invalid credentials or role.', 'error')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'role' in session and session['role'] == 'admin':
        return render_template('admin_dashboard.html', user=session['user'])
    return redirect(url_for('login'))

@app.route('/user_dashboard')
def user_dashboard():
    if 'role' in session and session['role'] == 'user':
        return render_template('user_dashboard.html', user=session['user'])
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/about')
def about():
    return render_template('about.html')


if __name__ == '__main__':
    app.run(debug=True)

