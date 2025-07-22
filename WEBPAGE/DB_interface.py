import sqlite3
db = "DB.db"

def connect():
    try:
        conn = sqlite3.connect(db)
        return conn
    except sqlite3.Error as e:
        print(f"Error in connect: {e}")
        return None

def close(conn):
    if conn:
        conn.close()

def get_data(query, params=()):
    conn = connect()
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        close(conn)
        return rows
    except sqlite3.Error as e:
        print(f"Error in get_data: {e}")
        close(conn)
        return []
    
def execute_query(query, params=()):
    conn = connect()
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        close(conn)
    except sqlite3.Error as e:
        print(f"Error in execute_query: {e}")
        close(conn)