import socket
import DB_interface
from enc import hash_password as encrypt
import datetime
from datetime import datetime, timedelta
import secrets
from shapely.geometry import Point, Polygon
from flask import Flask, request, render_template, redirect, url_for, session, make_response

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
    DB_interface.execute_query("INSERT INTO SIGNS (UserID, DeviceID, Date, DeviceName) VALUES (?, ?, ?, ?)", (user_id, Mac, datetime.now(), "WEBSITE"))

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
    locationID = DB_interface.get_data("SELECT LocationID FROM LOCATIONS WHERE LocationName = ?", (location,))

    if locationID:
        locationID = locationID[0][0]
    else:
        return

    now = datetime.now()
    d = now.weekday()
    t = now.strftime("%H:%M")
    w = 1 if (now.isocalendar().week % 2) == 1 else 2
    DB_interface.execute_query("UPDATE ALTERATION SET LocationID = ?, Start = ?, Day = ?, Week = ? WHERE UserID = ? AND EventID = 1", (locationID, t, d, w, user_id))

def account_type(user_id):
    account_type = DB_interface.get_data("SELECT RoleID FROM ACCOUNTS WHERE UserID = ?", (user_id,))
    if account_type:
        return account_type[0][0]
    return None



zone = {
    "Home": Polygon([
        (-1.2356403, 51.8233035),
        (-1.2354203, 51.8229257),
        (-1.2344489, 51.8229886),
        (-1.2346985, 51.8234195),
        (-1.2356323, 51.8233052)]),
    "DT": Polygon([
        (-1.2678601, 51.7773799),
        (-1.2679593, 51.7775135),
        (-1.2676348, 51.7776155),
        (-1.2673277, 51.7772413),
        (-1.2676066, 51.7771625),
        (-1.2678078, 51.7772670),
        (-1.2678561, 51.7773865)]),
    "Maths": Polygon([
        (-1.2683425, 51.7778901),
        (-1.2682325, 51.7777723),
        (-1.2679722, 51.7778105),
        (-1.2678434, 51.7776413),
        (-1.2675616, 51.7776562),
        (-1.2676662, 51.7779017),
        (-1.2678970, 51.7780245),
        (-1.2683506, 51.7778852)
    ]),
    "Old-library": Polygon([
        (-1.2682446, 51.7769319),
        (-1.2681748, 51.7769485),
        (-1.2681023, 51.7768606),
        (-1.2679118, 51.7769137),
        (-1.2679091, 51.7771012),
        (-1.2680862, 51.7771792),
        (-1.2682982, 51.7771095),
        (-1.2683078, 51.7770202),
        (-1.2682580, 51.7769353)
    ]),
    "Chemistry": Polygon([
        (-1.2685039, 51.7760657),
        (-1.2686837, 51.7760060),
        (-1.2685147, 51.7758052),
        (-1.2681684, 51.7759280),
        (-1.2685066, 51.7760657)
    ]),
    "Physics": Polygon([
        (-1.2683241, 51.7760674),
        (-1.2681899, 51.7759081),
        (-1.2679054, 51.7760209),
        (-1.2681094, 51.7762051),
        (-1.2683375, 51.7760640)
    ]),
    "Oxley": Polygon([
        (-1.2676164, 51.7769129),
        (-1.2680459, 51.7768001),
        (-1.2679493, 51.7766574),
        (-1.2675145, 51.7768101),
        (-1.2676197, 51.7769124)
    ]),
    "Music": Polygon([
        (-1.2693056, 51.7776259),
        (-1.2689110, 51.7777852),
        (-1.2693056, 51.7782929),
        (-1.2695981, 51.7782033),
        (-1.2693539, 51.7776209)
    ]),
    "PE": Polygon([
        (-1.2677604, 51.7763331),
        (-1.2675886, 51.7761821),
        (-1.2674168, 51.7762534),
        (-1.2675269, 51.7764094),
        (-1.2677604, 51.7763364)
    ]),
    "Humanity": Polygon([
        (-1.2672622, 51.7764747),
        (-1.2671401, 51.7763345),
        (-1.2673749, 51.7762565),
        (-1.2675038, 51.7763943),
        (-1.2672636, 51.7764739)
    ]),
    "Biology": Polygon([
        (-1.2680632, 51.7762300),
        (-1.2679773, 51.7761354),
        (-1.2674324, 51.7762516),
        (-1.2675183, 51.7763976),
        (-1.2677353, 51.7763395),
        (-1.2680591, 51.7762258)
    ]),
    "NW":Polygon([
        (-1.2683557, 51.7777160),
        (-1.2684335, 51.7778454),
        (-1.2692602, 51.7775915),
        (-1.2691528, 51.7774472),
        (-1.2683477, 51.7777176)
    ])
}

#web functions
@app.route('/check_location', methods=['POST'])
def check_location():
    data = request.get_json()
    lat = data.get('a')
    lon = data.get('o')
    point = Point(lon, lat)
    for location_name, polygon in zone.items():
        if polygon.contains(point):
            update_current_location(session['user_id'], location_name)
            break

    return ''


@app.route('/update', methods=['GET', 'POST'])
def update():
    if request.method == 'POST':
        location = request.form['location']
        update_current_location(session['user_id'], location)
        return redirect(url_for('studentPage'))
    return render_template('update.html', locations=[i[0] for i in DB_interface.get_data("SELECT LocationName FROM LOCATIONS")])

#pages
@app.route('/sub/teacherTiles', methods=['GET'])
def teacher_tiles():
    limit = request.args.get("limit", "50")
    search_name = request.args.get("SearchName", "")
    houses = request.args.getlist("house")
    forms = request.args.getlist("form")

    sql = """
        SELECT
            ACCOUNTS.Image,
            ACCOUNTS.FirstName,
            ACCOUNTS.LastName,
            STUDENT_INFO.House,
            STUDENT_INFO.Form
        FROM
            ACCOUNTS
        JOIN
            STUDENT_INFO ON ACCOUNTS.UserID = STUDENT_INFO.UserID
        WHERE
            RoleID = 0
            AND (FirstName LIKE ? OR LastName LIKE ?)
    """

    params = [f"%{search_name}%", f"%{search_name}%"]

    if houses:
        placeholders = ','.join(['?'] * len(houses))
        sql += f" AND STUDENT_INFO.House IN ({placeholders})"
        params.extend(houses) # adds each item in list into list
    if forms:
        placeholders = ','.join(['?'] * len(forms))
        sql += f" AND STUDENT_INFO.Form IN ({placeholders})"
        params.extend(forms)

    sql += " ORDER BY LastName, FirstName LIMIT ?"
    params.append(limit)

    #DB and dealing with results
    people = [
        [dir.replace("\\", "/"), a, b, c, d]
        for dir, a, b, c, d in DB_interface.get_data(sql, tuple(params))
    ]

    return render_template('sub/teacherTiles.html', people=people)



@app.route('/adminPage', methods=['GET', 'POST'])
def adminPage():
    return render_template('adminPage.html')


@app.route('/teacherPage', methods=['GET', 'POST'])
def TeacherPage():
    if account_type(session['user_id']) == 2:
        return redirect(url_for('adminPage'))
    
    return render_template('teacherPage.html')


@app.route('/studentPage', methods=['GET', 'POST'])
def studentPage():
    if account_type(session['user_id']) != 0:
        return redirect(url_for('TeacherPage'))

    if request.method == 'POST':
        location = request.form['location']
        update_current_location(session['user_id'], location)

    now = datetime.now()
    d = now.weekday()
    t = now.strftime("%H:%M")
    w = 1 if (now.isocalendar().week % 2) == 1 else 2

    last=0
    next=0

    timeTable=get_combined_timetable(session['user_id'])
    for i, (day, start, end, subject, location, week, teacher) in enumerate(timeTable):
        if (day == d) and (week == w) and (start <= t <= end if end else '24:00'):
            last = i - 1 if i - 1 >= 0 else None
            next = i + 1 if i + 1 < len(timeTable) else None

    return render_template(
        'studentPage.html',
        timeTable=timeTable,
        current_day=d,
        current_time=t,
        current_week=w,
        last=last,
        next=next,
        locations=[i[0] for i in DB_interface.get_data("SELECT LocationName FROM LOCATIONS")]
    )


@app.route('/login', methods=['GET', 'POST'])
def login():
    # remove old
    DB_interface.execute_query(
    "DELETE FROM REMEMBER_ME WHERE ExpiryDate <= CURRENT_TIMESTAMP"
    )


    if request.method == 'POST':
        token = request.cookies.get('remember_token')
        if token:
            user = DB_interface.get_data("SELECT UserID FROM REMEMBER_ME WHERE Token = ? AND ExpiryDate > CURRENT_TIMESTAMP", (token,))
            if user:
                session['user_id'] = user[0][0]
                return redirect(url_for('studentPage'))



        email_type = request.form['emailType']
        remember_me = request.form.get('rememberMe', 'off') == 'on'
        enc = encrypt(request.form['password'])
        user_id = check_login(request.form["email"], enc, email_type)

        if user_id:
            session['user_id'] = user_id
            response = make_response(redirect(url_for('studentPage')))

            if remember_me:
                token = secrets.token_hex(32)
                expires = datetime.now() + timedelta(days=30)

                DB_interface.execute_query(
                    "INSERT INTO REMEMBER_ME (UserID, Token, ExpiryDate) VALUES (?, ?, ?)",
                    (user_id, token, expires)
                )
                response.set_cookie('remember_token', token, max_age=60*60*24*30)

            return response
        else:
            return render_template('login.html', error="Invalid email or password")
    return render_template('login.html')


@app.route('/')
def redirect_to_login():
    return redirect("/login")


@app.errorhandler(404)
def not_found(e):
    return render_template("404.html")


#start the app
if __name__ == '__main__':
    #app.run(host=my_ip, port=5000, debug=True, threaded=True)
    app.run(host='localhost', port=8000, debug=True, threaded=True)