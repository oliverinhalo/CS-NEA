import sqlite3
db = "DB.db"

def connect():
    try: # tries to connect
        conn = sqlite3.connect(db) # to the database
        return conn # returns the connection as an pointer
    except sqlite3.Error as e: # if it failes due to an error
        print(f"Error in connect: {e}") # prints the error
        return None

def close(conn): # closes the connection
    if conn: # if the connection exists
        conn.close() # close it

def get_data(query, params=()): 
    conn = connect() # connects to the DB
    try:
        cursor = conn.cursor() # creates a cursor object
        cursor.execute(query, params) # executes the query with params
        rows = cursor.fetchall() # fetches all the data
        close(conn) # closes the connection
        return rows # returns the data
    except sqlite3.Error as e: # if it failes due to an error
        print(f"Error in get_data: {e}") # prints the error
        close(conn) # closes the connection
        return [] # returns an empty list
    
def execute_query(query, params=()):
    conn = connect() # connects to the DB
    try:
        cursor = conn.cursor() # creates a cursor object
        cursor.execute(query, params) # executes the query with params
        conn.commit() # commits the changes
        close(conn) # closes the connection
        return True
    except sqlite3.Error as e: # if it failes due to an error
        print(f"Error in execute_query: {e}") # prints the error
        close(conn) # closes the connection
        return False
    
def get_data_colums(query, params=()): 
    conn = connect() # connects to the DB
    try:
        cursor = conn.cursor() # creates a cursor object
        cursor.execute(query, params) # executes the query with params
        rows = cursor.fetchall() # fetches all the data
        columns = [desc[0] for desc in cursor.description] # gets the column names
        close(conn) # closes the connection
        return rows, columns # returns the data and column names
    except sqlite3.Error as e: # if it failes due to an error
        print(f"Error in get_data: {e}") # prints the error
        close(conn) # closes the connection
        return [], [] # returns 2 empty lists