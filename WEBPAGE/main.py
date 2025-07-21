import socket
import DB_interface
import hashlib
import datetime
from datetime import datetime
from flask import Flask, request, render_template, redirect, url_for, session
app = Flask(__name__)
app.secret_key = 'user_id'

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.connect(("8.8.8.8", 80))
    my_ip=s.getsockname()[0]


def check_login(Email, password, email_type):
    email_type = "SchoolEmail" if email_type == "school" else "HomeEmail"
    user_id = DB_interface.get_data(f"SELECT UserID FROM ACCOUNTS WHERE {email_type} = ? AND Password = ?", (Email, password))
    return user_id[0][0] if user_id else None

def add_to_remember_me(user_id):
    Mac = request.headers.get('X-Forwarded-For', request.remote_addr)
    DB_interface.execute_query("INSERT INTO SIGNS (UserID, MAC_ID, Date, DeviceID) VALUES (?, ?, ?, ?)", (user_id, Mac, datetime.now(), "WEBSITE"))

def get_time_table(user_id):
    timeTableID = DB_interface.get_data("SELECT TimeTableID FROM STUDENT_INFO WHERE UserID = ?", (user_id,))[0][0]
    data = DB_interface.get_data("""
    SELECT 
        TIMETABLE.Day,
        TIMETABLE.Start,
        TIMETABLE.End,
        SUBJECTS.Name,
        LOCATIONS.LocationName,
        TIMETABLE.Week,
        substr(ACCOUNTS.FirstName, 1, 1) || '. ' || ACCOUNTS.LastName
    FROM 
        TIMETABLE
    JOIN 
        SUBJECTS ON TIMETABLE.SubjectID = SUBJECTS.SubjectID
    JOIN 
        LOCATIONS ON TIMETABLE.LocationID = LOCATIONS.LocationID
    JOIN 
        ACCOUNTS ON SUBJECTS.UserID = ACCOUNTS.UserID
    WHERE 
        TIMETABLE.TimeTableID = ?
    ORDER BY 
        TIMETABLE.Week, TIMETABLE.Day, TIMETABLE.Start;

        """, (timeTableID,))
    return data

@app.route('/home', methods=['GET'])
def home():
    return render_template('home.html', timeTable=get_time_table(session['user_id']))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email_type = request.form['emailType'] 
        remember_me = request.form.get('rememberMe', 'off') == 'on'
        user_id = check_login(request.form["email"], hashlib.sha256((request.form['password']).encode()).hexdigest(), email_type)
        if user_id:
            if remember_me:
                add_to_remember_me(user_id)
            session['user_id'] = user_id
            return redirect(url_for('home'))
        else:
            return render_template('login.html', error="Invalid email or password")
    return render_template('login.html', error=False)

@app.route('/')
def redirect_to_login():
    return redirect("/login", code=302)

@app.errorhandler(404)
def not_found(e):
    return render_template("404.html")

if __name__ == '__main__':
    app.run(host=my_ip, port=5000, debug=True, threaded=False)