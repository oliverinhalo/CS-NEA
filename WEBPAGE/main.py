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

def get_alteration(user_id):
    alteration = DB_interface.get_data(
        """
        SELECT 
            LOCATIONS.LocationName, 
            ALTERATION.Start, 
            ALTERATION.End, 
            ALTERATION.Day, 
            ALTERATION.Week,
            ALTERATION.Title
        FROM
            ALTERATION
        JOIN
            LOCATIONS ON ALTERATION.LocationID = LOCATIONS.LocationID
        WHERE
            ALTERATION.UserID = ?""", 
        (user_id,)
        )
    return alteration

def get_combined_timetable(user_id):
    tt = get_time_table(user_id)
    alterations = get_alteration(user_id)
    timetable = []

    for location, start, end, day, week, title in alterations:
        entry = (
            day,
            start,
            end,
            title,
            location,
            week,
            "N/A"
        )
        timetable.append(entry)
    for day, start, end, subject, location, week, teacher in tt:
        entry = (
            day,
            start,
            end,
            subject,
            location,
            week,
            teacher
        )
        timetable.append(entry)

    return sorted(timetable, key=lambda x: (x[5], x[0], x[1]))

def update_current_location(user_id, location):
    locationID = DB_interface.get_data("SELECT LocationID FROM LOCATIONS WHERE LocationName = ?", (location,))[0][0]
    now = datetime.now()
    d = now.weekday()
    t = now.strftime("%H:%M")
    w = 1 if (now.isocalendar().week % 2) == 1 else 2
    DB_interface.execute_query("UPDATE ALTERATION SET LocationID = ?, Start = ?, Day = ?, Week = ? WHERE UserID = ? AND EventID = 1", (locationID, t, d, w, user_id))

@app.route('/update', methods=['GET', 'POST'])
def update():
    if request.method == 'POST':
        location = request.form['location']
        update_current_location(session['user_id'], location)
        return redirect(url_for('home'))
    return render_template('update.html', locations=[i[0] for i in DB_interface.get_data("SELECT LocationName FROM LOCATIONS")])

@app.route('/home', methods=['GET'])
def home():
    now = datetime.now()
    d = now.weekday()
    t = now.strftime("%H:%M")
    w = 1 if (now.isocalendar().week % 2) == 1 else 2

    return render_template(
        'home.html',
        timeTable=get_combined_timetable(session['user_id']),
        alteration=get_alteration(session['user_id']),
        current_day=d,
        current_time=t,
        current_week=w
        )

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
    return redirect("/login")

@app.errorhandler(404)
def not_found(e):
    return render_template("404.html")

if __name__ == '__main__':
    app.run(host=my_ip, port=5000, debug=True, threaded=False)