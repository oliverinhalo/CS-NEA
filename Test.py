import DB_interface
DB_interface.execute_query("DELETE FROM ACCOUNTS")
DB_interface.execute_query("DELETE FROM LOCATIONS")
DB_interface.execute_query("DELETE FROM SIGNS")
DB_interface.execute_query("DELETE FROM STUDENT_INFO")
DB_interface.execute_query("DELETE FROM SUBJECTS")
DB_interface.execute_query("DELETE FROM TIMETABLE")