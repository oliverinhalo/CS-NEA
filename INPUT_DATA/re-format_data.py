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

def is_gender_match(image, target_gender, min_age=16, confidence_threshold=90):
    try:
        # Convert BGR to RGB as DeepFace expects RGB
        img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Analyze gender and age
        analysis = DeepFace.analyze(
            img_rgb,
            actions=['gender', 'age'],
            enforce_detection=False,
            detector_backend='retinaface'  # can try mtcnn, ssd, etc.
        )

        # Handle if multiple faces are returned
        if isinstance(analysis, list):
            analysis = analysis[0]

        # Extract gender info
        gender_pred = analysis.get('gender', None)
        age = analysis.get('age', None)

        if not gender_pred or age is None:
            return False

        # Gender can be a dict or string
        if isinstance(gender_pred, dict):
            predicted_gender = max(gender_pred, key=gender_pred.get)
            confidence = gender_pred[predicted_gender]
            if confidence < confidence_threshold:
                return False  # Not confident enough
        elif isinstance(gender_pred, str):
            predicted_gender = gender_pred
            confidence = 100  # Assume full confidence if not a dict
        else:
            return False

        # Normalize gender
        if predicted_gender.lower().startswith('m'):
            predicted_gender_char = 'm'
        elif predicted_gender.lower().startswith(('w', 'f')):
            predicted_gender_char = 'f'
        else:
            return False  # Unknown or ambiguous gender

        # Check minimum age
        if age < min_age:
            return False

        # Final gender match check
        return predicted_gender_char == target_gender.lower()

    except Exception as e:
        print("Error in is_gender_match_strict:", e)
        return False
    try:
        # DeepFace expects RGB images
        img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        analysis = DeepFace.analyze(img_rgb, actions=['gender'], enforce_detection=False)

        # DeepFace output format varies by version:
        # Sometimes analysis is a list (if multiple faces), sometimes a dict (single face)
        if isinstance(analysis, list):
            analysis = analysis[0]

        gender_pred = analysis.get('gender', None)

        # Debug print to check output format (uncomment if needed)
        # print("DeepFace gender output:", gender_pred)

        if isinstance(gender_pred, dict):
            # Example: {'Woman': 99.8, 'Man': 0.2}
            predicted_gender = max(gender_pred, key=gender_pred.get)
        elif isinstance(gender_pred, str):
            predicted_gender = gender_pred
        else:
            # Unknown format
            return False

        # Normalize predicted gender to single char for matching
        predicted_gender_char = None
        if predicted_gender.lower().startswith('m'):
            predicted_gender_char = 'm'
        elif predicted_gender.lower().startswith('w') or predicted_gender.lower().startswith('f'):
            # 'Woman' or 'Female' both considered female
            predicted_gender_char = 'f'
        else:
            # Unknown gender string
            return False

        return predicted_gender_char == target_gender.lower()

    except Exception as e:
        print(f"Gender detection failed: {e}")
        return False

# Load your Excel data and convert to JSON/dict
Pupil_data = pd.read_excel('INPUT_DATA/Pupil_data.xlsx')
Pupil_data = json.loads(Pupil_data.to_json(orient='records'))

Pupil_Timetable_data = pd.read_excel('INPUT_DATA/Pupil_Timetable_data.xlsx')
Pupil_Timetable_data = json.loads(Pupil_Timetable_data.to_json(orient='records'))

Set_Timetable_data = pd.read_excel('INPUT_DATA/Set_Timetable_data.xlsx')
Set_Timetable_data = json.loads(Set_Timetable_data.to_json(orient='records'))

# Stringify keys
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


# Load first and last names
with open("INPUT_DATA/FirstNames.txt", "r") as file:
    first_names = [name.strip() for name in file.readlines()]

with open("INPUT_DATA/LastNames.txt", "r") as file:
    last_names = [name.strip() for name in file.readlines()]

pwo = PasswordGenerator()
faces_dir = "faces"
os.makedirs(faces_dir, exist_ok=True)

for pupil in Pupil_data:
    gender = pupil['Gender'].lower()  # 'm' or 'f'
    g = "m" if gender == "f" else "f"

    # Pick a first name that matches gender (roughly)
    while g != gender:
        first = random.choice(first_names)
        det = determine_gender(first)
        if det != 'unknown':
            g = "m" if det == "male" else "f"

    last = random.choice(last_names)
    email = f"{first.lower()}.{last.lower()}@school.co.uk"
    password = hash(pwo.generate())

    attempts = 0
    while True:
        face = get_random_face_image()
        if is_gender_match(face, gender):
            break
        attempts += 1
        if attempts > 10:
            print(f"Warning: Couldn't find a face for gender '{gender}' after 10 attempts.")
            break

    email_hash = hashlib.sha256(email.encode()).hexdigest()
    image_path = os.path.join(faces_dir, f"{email_hash}.png")
    cv2.imwrite(image_path, face)

    relative_path = os.path.relpath(image_path)

    DB_interface.execute_query(
        "INSERT INTO ACCOUNTS (UserID, Gender, RoleID, FirstName, LastName, SchoolEmail, Password, Image) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (pupil['Pupil ID'], gender, 0, first, last, email, password, relative_path)
    )
