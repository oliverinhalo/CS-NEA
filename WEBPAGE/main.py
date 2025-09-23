import socket
import DB_interface
from enc import hash_password as encrypt
import datetime
from datetime import datetime, timedelta
import secrets
from shapely.geometry import Point, Polygon
from fileinput import filename
from PIL import Image
import logging
import smtplib
import random
import os
from dotenv import load_dotenv
from flask import Flask, flash, request, render_template, redirect, url_for, session, make_response

logger = logging.getLogger('my_logger')
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

f = logging.FileHandler('app.log')
c = logging.StreamHandler()
f.setLevel(logging.INFO)
f.setFormatter(formatter)
c.setLevel(logging.INFO)
c.setFormatter(formatter)

logger.addHandler(f)
logger.addHandler(c)


app = Flask(__name__)
app.secret_key = 'user_id'


with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.connect(("8.8.8.8", 80))
    my_ip=s.getsockname()[0]


load_dotenv()


def check_login(Email, password, email_type):
    email_type = "SchoolEmail" if email_type == "school" else "HomeEmail"
    user_id = DB_interface.get_data(f"SELECT UserID FROM ACCOUNTS WHERE {email_type} = ? AND Password = ?", (Email, password))
    return user_id[0][0] if user_id else None

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
    timettable = get_time_table(user_id)
    alterations = get_alteration(user_id)
    final_timetable = []

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
        final_timetable.append(entry)
    for day, start, end, subject, location, week, teacher in timettable:
        entry = (
            day,
            start,
            end,
            subject,
            location,
            week,
            teacher
        )
        final_timetable.append(entry)
    return sorted(final_timetable, key=lambda x: (x[5], x[0], x[1]))

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

def update_password(user_id, current_password, new_password):
    if not DB_interface.get_data("SELECT UserID FROM ACCOUNTS WHERE UserID = ? AND Password = ?", (user_id, current_password)):
        return False
    DB_interface.execute_query("""
        UPDATE ACCOUNTS SET Password = ? WHERE UserID = ? AND Password = ?
    """, (new_password, user_id, current_password))
    return True

def send_email_code(to_email, code):
    to_email=os.environ.get('email') # for testing
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(os.environ.get('email'), os.environ.get('app_password'))
            message = f"Subject: Your MFA Code\n\nYour verification code is: {code}"
            server.sendmail(os.environ.get('email'), to_email, message)
    except Exception as e:
        print(f"Email send error: {e}")


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
    "Humanity": Polygon([
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
    "Maths": Polygon([
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


@app.route('/logout')
def logout():
    token = request.cookies.get('rememberToken')
    if token:
        DB_interface.execute_query(
            "DELETE FROM REMEMBER_ME WHERE Token = ?", (token,)
        )

    #clear data
    session.clear()

    resp = make_response(redirect(url_for('login')))
    resp.set_cookie('rememberToken', '', expires=0)
    return resp



#pages
@app.route("/page")
def page():
    print("Page requested")
    requested_page = request.args.get("page")
    logging.debug(f"Requested page: {requested_page}")
    return render_template(f"{requested_page}.html")

@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if request.method == 'POST':
        current_password = encrypt(request.form['current_password'])
        new_password = encrypt(request.form['new_password'])
        confirm_password = encrypt(request.form['confirm_password'])

        if new_password == confirm_password:
            if update_password(session['user_id'], current_password, new_password):
                print("Password updated successfully")
                return redirect(url_for('studentPage'))
            else:
                print("Password update failed")
                return redirect(url_for('change_password'))

    return redirect(url_for('studentPage'))

@app.route('/change_image', methods=['GET', 'POST'])
def change_image():
    if request.method == 'POST':
        img = request.files['imageUpload']
        f_name=encrypt(str(session['user_id'])) + ".png"
        img.save("WEBPAGE/static/img/faces/" + f_name)

        image = Image.open("WEBPAGE/static/img/faces/" + f_name)
        image = image.convert("RGB")
        image = image.crop((0, 0, min(image.size), min(image.size)))
        image = image.resize((150, 150))
        image = image.rotate(-90, expand=True)
        image.save("WEBPAGE/static/img/faces/" + f_name, "PNG")

        DB_interface.execute_query(
            "UPDATE ACCOUNTS SET Image = ? WHERE UserID = ?",
            (f"faces\\{f_name}", session['user_id'])
        )
        return redirect(url_for('studentPage'))
    return render_template('change_image.html')

@app.route('/add_account', methods=['GET', 'POST'])
def add_account():
    response=False
    if request.method == 'POST':
        first_name = request.form['firstName']
        last_name = request.form['lastName']
        gender = request.form['gender']
        email = request.form['email']
        role = request.form['role']
        img = request.files['imageUpload']
        f_name=encrypt(email) + ".png"
        img.save("WEBPAGE/static/img/faces/" + f_name)

        image = Image.open("WEBPAGE/static/img/faces/" + f_name)
        image = image.convert("RGB")
        image = image.crop((0, 0, min(image.size), min(image.size)))
        image = image.resize((150, 150))
        image = image.rotate(-90, expand=True)
        image.save("WEBPAGE/static/img/faces/" + f_name, "PNG")

        response = DB_interface.execute_query(
            "INSERT INTO ACCOUNTS (FirstName, LastName, Gender, SchoolEmail, RoleID, Image) VALUES (?, ?, ?, ?, ?, ?)",
            (first_name, last_name, gender, email, role, f"faces\\{f_name}")
        )
    if not response:
        print("Account Failed to add successfully!")
        flash("Account Failed to add successfully!", "error")
        return redirect(url_for('adminAddAccount'))
    else:
        flash("Account added successfully!", "success")
        return redirect(url_for('adminAddAccount'))
    
@app.route('/sub/adminAddAccount', methods=['GET', 'POST'])
def adminAddAccount():
    return render_template('sub/adminAddAccount.html')

@app.route('/sub/adminRemoveAccount', methods=['GET', 'POST'])
def adminRemoveAccount():
    if request.method == 'POST':
        email = request.form['email']
        del_type = request.form['del_type']
        if del_type == "True":
            image = DB_interface.get_data("select Image from accounts where schoolemail = ?", (email,))
            if image and image[0][0]:
                try:
                    os.remove("WEBPAGE/static/" + image[0][0].replace("\\", "/"))
                except Exception as e:
                    print(f"Error deleting image: {e}")

            response = DB_interface.execute_query(
                "DELETE FROM ACCOUNTS WHERE SchoolEmail = ?;" \
                "DELETE FROM STUDENT_INFO WHERE UserID NOT IN (SELECT UserID FROM ACCOUNTS);" \
                "DELETE FROM TEACHER_INFO WHERE UserID NOT IN (SELECT UserID FROM ACCOUNTS);" \
                "DELETE FROM TIMETABLE WHERE UserID NOT IN (SELECT UserID FROM ACCOUNTS);" \
                "DELETE FROM ALTERATION WHERE UserID NOT IN (SELECT UserID FROM ACCOUNTS);" \
                "DELETE FROM REMEMBER_ME WHERE UserID NOT IN (SELECT UserID FROM ACCOUNTS);",
                (email,)
            )
            if not response:
                return redirect(url_for('adminRemoveAccount'))
            else:
                return redirect(url_for('adminRemoveAccount'))
        else:
            response = DB_interface.execute_query(
                "DELETE FROM ACCOUNTS WHERE SchoolEmail = ?",
                (email,)
            )
            if not response:
                return redirect(url_for('adminRemoveAccount'))
            else:
                return redirect(url_for('adminRemoveAccount'))
        
    return render_template('sub/adminRemoveAccount.html')

@app.route('/sub/teacherList', methods=['GET'])
def teacher_list():
    return render_template('sub/teacherList.html')


@app.route('/sub/teacherTiles', methods=['GET'])
def teacher_tiles():
    now = datetime.now()
    d = now.weekday()
    t = now.strftime("%H:%M")
    w = 1 if (now.isocalendar().week % 2) == 1 else 2

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
            STUDENT_INFO.Form,
            SUBJECTS.Name
        FROM
            ACCOUNTS
        JOIN
            STUDENT_INFO ON ACCOUNTS.UserID = STUDENT_INFO.UserID
        JOIN
            TIMETABLE ON STUDENT_INFO.TimeTableID = TIMETABLE.TimeTableID
        JOIN
            SUBJECTS ON TIMETABLE.SubjectID = SUBJECTS.SubjectID
        WHERE
            (TIMETABLE.Start <= ?
            AND TIMETABLE.End >= ?
            AND TIMETABLE.Day = ?
            AND TIMETABLE.Week = ?)
            AND RoleID = 0
            AND (FirstName LIKE ? OR LastName LIKE ?)
    """
    t="08:35" # for testing
    params = [t, t, d, w, f"%{search_name}%", f"%{search_name}%"]

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
    people = DB_interface.get_data(sql, tuple(params))


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


@app.route('/multi_factor_auth', methods=['GET', 'POST'])
def mfa():
    if request.method == 'POST':
        code = request.form['code']
        user_id = session.get('pending_user')
        if user_id and session["mfa_code"] == code:
            session.pop('pending_user', None)
            session.pop('mfa_code', None)
            return redirect(url_for('studentPage'))
        else:
            return render_template('multi_factor_auth.html', 
                                   email=session.get('pending_email'), 
                                   emailType=session.get('pending_emailType'),
                                   error="Invalid code")
    
    return render_template('multi_factor_auth.html', 
                           email=session.get('pending_email'), 
                           emailType=session.get('pending_emailType'))


@app.route('/login', methods=['GET', 'POST']) 
def login():
    # remove old
    DB_interface.execute_query(
        "DELETE FROM REMEMBER_ME WHERE ExpiryDate <= CURRENT_TIMESTAMP"
    )

    token = request.cookies.get('rememberToken')
    print(f"Token from cookie: {token}")
    if token:
        user = DB_interface.get_data(
            "SELECT UserID FROM REMEMBER_ME WHERE Token = ? AND ExpiryDate > CURRENT_TIMESTAMP",
            (token,)
        )
        if user:
            session['user_id'] = user[0][0]
            return make_response(redirect(url_for('studentPage')))

    # check for cookie token
    if request.method == 'POST':
        # get inputs button
        emailType = request.form['emailType']
        email = request.form["email"]
        remember_me = request.form.get('rememberMe', 'off') == 'on'
        enc = encrypt(request.form['password'])
        user_id = check_login(email, enc, emailType)

        if user_id:
            session['user_id'] = user_id

            # store login info for MFA
            session['pending_user'] = user_id
            session['pending_email'] = email
            session['pending_emailType'] = emailType

            # MFA code + send
            code = str(random.randint(100000, 999999))
            session['mfa_code'] = code
            send_email_code(email, code)

            # redirect to MFA page
            resp = make_response(redirect(url_for('mfa')))

            # handle Remember Me
            if remember_me:
                token = secrets.token_hex(32)
                expires = datetime.now() + timedelta(days=30)

                DB_interface.execute_query(
                    "INSERT INTO REMEMBER_ME (UserID, Token, ExpiryDate) VALUES (?, ?, ?)",
                    (user_id, token, expires)
                )
                resp.set_cookie('rememberToken', token, max_age=60*60*24*30)

            return resp
        else:
            return render_template('login.html', error="Invalid email or password")

    return render_template('login.html')


@app.route('/')
def redirect_to_login():
    return redirect("/login")


@app.errorhandler(404)
def not_found(e):
    logging.warning(f"404 error: {e}")
    return render_template("404.html")


#start the app
if __name__ == '__main__':
    #logging.info(f"Starting app on http://{my_ip}:5000")
    #app.run(host=my_ip, port=5000, debug=True, threaded=True)
    logging.info(f"Starting app on http://localhost:8000")
    app.run(host='localhost', port=8000, debug=True, threaded=True)