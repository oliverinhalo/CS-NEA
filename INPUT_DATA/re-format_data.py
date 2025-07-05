import pandas as pd
import json

Pupil_data = pd.read_excel('INPUT_DATA/Pupil_data.xlsx')
Pupil_data = Pupil_data.to_json(orient='records')
Pupil_data = json.loads(Pupil_data)

Pupil_Timetable_data = pd.read_excel('INPUT_DATA/Pupil_Timetable_data.xlsx')
Pupil_Timetable_data = Pupil_Timetable_data.to_json(orient='records')
Pupil_Timetable_data = json.loads(Pupil_Timetable_data)

Set_Timetable_data = pd.read_excel('INPUT_DATA/Set_Timetable_data.xlsx')
Set_Timetable_data = Set_Timetable_data.to_json(orient='records')
Set_Timetable_data = json.loads(Set_Timetable_data)


for i in range(len(Pupil_Timetable_data)):
    Pupil_Timetable_data[i]['Pupil Code'] = str(Pupil_Timetable_data[i]['Pupil Code'])
    Pupil_Timetable_data[i]['Set Code'] = str(Pupil_Timetable_data[i]['Set Code'])
    Pupil_Timetable_data[i]['Subject'] = str(Pupil_Timetable_data[i]['Subject'])
    Pupil_Timetable_data[i]['Teacher'] = str(Pupil_Timetable_data[i]['Teacher'])

for i in range(len(Pupil_data)):
    Pupil_data[i]['Pupil ID'] = str(Pupil_data[i]['Pupil ID'])
    Pupil_data[i]['Form'] = str(Pupil_data[i]['Form'])
    Pupil_data[i]['Boarding House'] = str(Pupil_data[i]['Boarding House'])
    Pupil_data[i]['Gender'] = str(Pupil_data[i]['Gender'])
    
for i in range(len(Set_Timetable_data)):
    Set_Timetable_data[i]['Set Code'] = str(Set_Timetable_data[i]['Set Code'])
    Set_Timetable_data[i]['Classroom'] = str(Set_Timetable_data[i]['Classroom'])
    Set_Timetable_data[i]['Period ID'] = str(Set_Timetable_data[i]['Period ID'])

print(Pupil_data)
print(Pupil_Timetable_data)
print(Set_Timetable_data)