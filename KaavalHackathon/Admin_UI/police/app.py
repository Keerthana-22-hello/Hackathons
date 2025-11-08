from flask import Flask, render_template, request, redirect, url_for,flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "supersecretkey123"
# Function to get database connection
def get_db_connection():
    conn = sqlite3.connect('police_dashboard.db')
    conn.row_factory = sqlite3.Row
    return conn

# Initialize database and create tables if they don't exist
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cases (
            case_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            status TEXT NOT NULL,
            date_created TEXT NOT NULL,
            crime_type TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS personnel (
            personnel_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            role TEXT NOT NULL,
            joined_date TEXT NOT NULL
        )
    ''')
    # Example data (optional, only if empty)
    cursor.execute("SELECT COUNT(*) FROM cases")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO cases (title, status, date_created,crime_type) VALUES (?, ?, ?, ?)",
                       ("Robbery at Market Street", "Active", "2025-11-08","Theft"))
        cursor.execute("INSERT INTO cases (title, status, date_created,crime_type) VALUES (?, ?, ?, ?)",
                       ("Fraud Investigation", "Solved", "2025-11-01","Fraud"))
    cursor.execute("SELECT COUNT(*) FROM personnel")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO personnel (name, role, joined_date) VALUES (?, ?, ?)",
                       ("Officer Raj", "Detective", "2022-03-15"))
        cursor.execute("INSERT INTO personnel (name, role, joined_date) VALUES (?, ?, ?)",
                       ("Officer Priya", "Inspector", "2021-07-10"))
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def dashboard():
    conn = get_db_connection()
    cases = conn.execute('SELECT * FROM cases').fetchall()
    personnel = conn.execute('SELECT * FROM personnel').fetchall()
    conn.close()

    total_cases = len(cases)
    active_cases = len([c for c in cases if c['status'] == 'Active'])
    solved_cases = len([c for c in cases if c['status'] == 'Solved'])

    # Data for charts
    crime_types = ["Theft", "Assault", "Fraud", "Cybercrime"]
    crime_counts = [12, 19, 8, 5]  # Placeholder, can later map to actual data

    return render_template('dashboard.html', total_cases=total_cases,
                           active_cases=active_cases, solved_cases=solved_cases,
                           cases=cases, personnel=personnel,
                           crime_types=crime_types, crime_counts=crime_counts)
#add case from Route
@app.route('/add_case', methods=['GET', 'POST'])
def add_case():
    if request.method == 'POST':
        title = request.form['title']
        status = request.form['status']
        date_created = request.form['date_created']
        crime_type = request.form['crime_type']  # New field

        conn = get_db_connection()
        conn.execute('INSERT INTO cases (title, status, date_created, crime_type) VALUES (?, ?, ?, ?)',
                     (title, status, date_created, crime_type))
        conn.commit()
        conn.close()
        flash(f"Case '{title}' added successfully!")
        return redirect(url_for('dashboard'))
    return render_template('form.html', form_type='case')

#update personnel from route
@app.route('/update_personnel', methods=['GET', 'POST'])
def update_personnel():
    if request.method == 'POST':
        name = request.form['name']
        role = request.form['role']
        joined_date = request.form['joined_date']
        conn = get_db_connection()
        conn.execute('INSERT INTO personnel (name, role, joined_date) VALUES (?, ?, ?)',
                     (name, role, joined_date))
        conn.commit()
        conn.close()
        return redirect(url_for('dashboard'))
    return render_template('form.html', form_type='personnel')

if __name__ == '__main__':
    app.run(debug=True)
