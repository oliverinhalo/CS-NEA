import random
import pandas as pd
import json
import DB_interface
import gender_guesser.detector as gender_detector
from password_generator import PasswordGenerator
import os
import hashlib
import requests
import numpy as np
import cv2
from deepface import DeepFace
from datetime import datetime, timedelta

def determine_gender(name):
    guessed_gender = gender_detector.Detector().get_gender(name)
    if guessed_gender in ['mostly_male', 'mostly_female', 'andy']:
        return 'unknown'
    else:
        return guessed_gender

def get_random_face_image():
    response = requests.get("https://thispersondoesnotexist.com", timeout=5)
    if response.status_code == 200:
        image_array = np.asarray(bytearray(response.content), dtype=np.uint8)
        return cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    else:
        raise Exception("Failed to fetch image from thispersondoesnotexist.com")

def is_gender_match(image, target_gender, min_age=30):
    try:
        img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        analysis = DeepFace.analyze(
            img_rgb,
            actions=['gender', 'age'],
            enforce_detection=False,
            detector_backend='retinaface'
        )

        if isinstance(analysis, list):
            analysis = analysis[0]

        gender_pred = analysis.get('gender', None)
        age = analysis.get('age', None)

        if not gender_pred or age is None:
            return False

        if isinstance(gender_pred, dict):
            predicted_gender = max(gender_pred, key=gender_pred.get)
            confidence = gender_pred[predicted_gender]

            if confidence < 95:
                return False
        elif isinstance(gender_pred, str):
            predicted_gender = gender_pred
            confidence = 95
        else:
            return False

        predicted_gender_char = None
        if predicted_gender.lower().startswith('m'):
            predicted_gender_char = 'm'
        elif predicted_gender.lower().startswith(('f', 'w')):
            predicted_gender_char = 'f'
        else:
            return False

        if age > min_age:
            return False

        return predicted_gender_char == target_gender.lower()

    except Exception as e:
        print("Error in is_gender_match:", e)
        return False

# Load your Excel data and convert to JSON/dict
Pupil_data = pd.read_excel('INPUT_DATA/Pupil_data.xlsx')
Pupil_data = json.loads(Pupil_data.to_json(orient='records'))

Pupil_Timetable_data = pd.read_excel('INPUT_DATA/Pupil_Timetable_data.xlsx')
Pupil_Timetable_data = json.loads(Pupil_Timetable_data.to_json(orient='records'))

Set_Timetable_data = pd.read_excel('INPUT_DATA/Set_Timetable_data.xlsx')
Set_Timetable_data = json.loads(Set_Timetable_data.to_json(orient='records'))

for row in Pupil_Timetable_data:
    row['Pupil Code'] = str(row['Pupil Code'])
    row['Set Code'] = str(row['Set Code'])
    row['Subject'] = str(row['Subject'])
    row['Teacher'] = str(row['Teacher'])

for row in Pupil_data:
    row['Pupil ID'] = str(row['Pupil ID'])
    row['Form'] = str(row['Form'])
    row['Boarding House'] = str(row['Boarding House'])
    row['Gender'] = str(row['Gender'])

for row in Set_Timetable_data:
    row['Set Code'] = str(row['Set Code'])
    row['Classroom'] = str(row['Classroom'])
    row['Period ID'] = str(row['Period ID'])


with open("INPUT_DATA/FirstNames.txt", "r") as file:
    first_names = [name.strip() for name in file.readlines()]

with open("INPUT_DATA/LastNames.txt", "r") as file:
    last_names = [name.strip() for name in file.readlines()]

with open("INPUT_DATA/periods.json", "r") as file:
    periods = json.load(file)

pwo = PasswordGenerator()
faces_dir = "faces"
os.makedirs(faces_dir, exist_ok=True)


setup=False
if setup:
    DB_interface.execute_query("INSERT INTO EVENTS (Type) VALUES (?)", ("Academic Lesson",))
    DB_interface.execute_query("INSERT INTO EVENTS (Type) VALUES (?)", ("Music Lesson",))
    DB_interface.execute_query("INSERT INTO EVENTS (Type) VALUES (?)", ("Sport",))

    DB_interface.execute_query("INSERT INTO ROLES (RoleID, RoleName) VALUES (?, ?)", (0,"Pupil"))
    DB_interface.execute_query("INSERT INTO ROLES (RoleID, RoleName) VALUES (?, ?)", (1,"Teacher"))
    DB_interface.execute_query("INSERT INTO ROLES (RoleID, RoleName) VALUES (?, ?)", (2,"Admin"))

done = DB_interface.get_data("SELECT UserID FROM ACCOUNTS")
done = [str(x[0]) for x in done]
for pupil in Pupil_data:
    if pupil["Pupil ID"] in done:
        continue
    gender = pupil['Gender'].lower()  # 'm' or 'f'
    g = "m" if gender == "f" else "f"

    while g != gender:
        first = random.choice(first_names)
        det = determine_gender(first)
        if det != 'unknown':
            g = "m" if det == "male" else "f"

    last = random.choice(last_names)
    email = f"{first.lower()}.{last.lower()}@school.co.uk"
    password = pwo.generate()
    password = hashlib.sha256(password.encode()).hexdigest()

    attempts = 0
    while True:
        face = get_random_face_image()
        if is_gender_match(face, gender):
            break
        attempts += 1
        print("fail atempt", attempts)

    email_hash = hashlib.sha256(email.encode()).hexdigest()
    image_path = os.path.join(faces_dir, f"{email_hash}.png")
    cv2.imwrite(image_path, face)

    relative_path = os.path.relpath(image_path)
    

    
    TTID = pupil['Pupil ID']

    for i in Pupil_Timetable_data:
        if i["Pupil Code"] == TTID:
            set_code = i["Set Code"]
            for set in Set_Timetable_data:
                if set["Set Code"] == set_code:
                    location = set["Classroom"]
                    period = set["Period ID"]

                    data = periods[period]
                    start, end, day, week = data['start'], data['end'], data['day'], data['week']
                    
                    
                    LocationID = DB_interface.get_data("SELECT LocationID FROM LOCATIONS WHERE LocationName = ?", (location,))
                    if LocationID == []:
                        DB_interface.execute_query("INSERT INTO LOCATIONS (LocationName) VALUES (?)", (location,))
                        LocationID = DB_interface.get_data("SELECT LocationID FROM LOCATIONS WHERE LocationName = ?", (location,))

                    LocationID = LocationID[0][0]
                    
                    subject_name = i["Subject"]
                    teacher = i["Teacher"]
                    while DB_interface.get_data("SELECT SubjectID FROM SUBJECTS WHERE Name = ? AND UserID = ? AND EventID = ?", (subject_name, teacher, 0)) == []:
                        DB_interface.execute_query("INSERT INTO SUBJECTS (Name, UserID, EventID) VALUES (?, ?, ?)", (subject_name, teacher, 0))
                    
                    SubjectID = DB_interface.get_data("SELECT SubjectID FROM SUBJECTS WHERE Name = ? AND UserID = ? AND EventID = ?", (subject_name, teacher, 0))
                    SubjectID = SubjectID[0][0]

                    
                    DB_interface.execute_query(
                    "INSERT INTO TIMETABLE (TimeTableID, LocationID, SubjectID, Start, End, Day, Week) VALUES (?,?,?,?,?,?,?)",
                    (TTID, LocationID, SubjectID, start, end, day, week)
                    )
                    


    DB_interface.execute_query(
        "INSERT INTO ACCOUNTS (UserID, Gender, RoleID, FirstName, LastName, SchoolEmail, Password, Image) VALUES (?,?,?,?,?,?,?,?)",
        (pupil['Pupil ID'], gender, 0, first, last, email, password, relative_path)
    )

    DB_interface.execute_query(
        "INSERT INTO STUDENT_INFO (UserID, Form, House, TimeTableID) VALUES (?,?,?,?)",
        (pupil['Pupil ID'], pupil['Form'], pupil['Boarding House'], TTID)
        )
