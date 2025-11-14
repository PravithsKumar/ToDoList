from flask import Flask, render_template, redirect, url_for, request, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'secret'


conn1 = sqlite3.connect('USERS.db')
cursor1 = conn1.cursor()
cursor1.execute("""
    CREATE TABLE IF NOT EXISTS USERS(
        email TEXT PRIMARY KEY,
        password TEXT NOT NULL
    )
""")
conn1.commit()
conn1.close()


conn2 = sqlite3.connect('TASKS.db')
cursor2 = conn2.cursor()
cursor2.execute("""
    CREATE TABLE IF NOT EXISTS TASKS(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL,
        task TEXT NOT NULL
    )
""")
conn2.commit()
conn2.close()

# ----- Helper functions -----
def add_user(email, password):
    conn = sqlite3.connect('USERS.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO USERS(email, password) VALUES(?, ?)", (email, password))
    conn.commit()
    conn.close()

def get_user(email, password):
    conn = sqlite3.connect('USERS.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM USERS WHERE email=? AND password=?", (email, password))
    user = cursor.fetchone()
    conn.close()
    return user

def add_task(email, task):
    conn = sqlite3.connect('TASKS.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO TASKS(email, task) VALUES(?, ?)", (email, task))
    conn.commit()
    conn.close()

def get_tasks(email):
    conn = sqlite3.connect('TASKS.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, task FROM TASKS WHERE email=?", (email,))
    tasks = cursor.fetchall()
    conn.close()
    return tasks

def delete_task(task_id):
    conn = sqlite3.connect('TASKS.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM TASKS WHERE id=?", (task_id,))
    conn.commit()
    conn.close()


@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = get_user(email, password)
        if user:
            session['user'] = email
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', msg='Invalid email or password')

    return render_template('login.html')

@app.route('/signIn', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = get_user(email, password)
        if user:
            return render_template('signIn.html', msg='User already exists')

        add_user(email, password)
        return redirect(url_for('login'))

    return render_template('signIn.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))

    email = session['user']

    if request.method == 'POST':
        task = request.form['task']
        if task.strip() != '':
            add_task(email, task)

    tasks = get_tasks(email)
    return render_template('home.html', email=email, tasks=tasks)

@app.route('/delete/<int:id>')
def delete(id):
    if 'user' not in session:
        return redirect(url_for('login'))
    delete_task(id)
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)



