import sqlite3
import os

home_dir = os.path.expanduser("~")

def drop_table():
    connection = sqlite3.connect(f'{home_dir}/.pd.db')  # 'example.db' is the database file
    cursor = connection.cursor()
    cursor.execute('DROP TABLE incidents;')
    connection.commit()
    connection.close()

def init_db():
    if os.path.exists(f'{home_dir}/.pd.db'):
        try:
            connection = sqlite3.connect(f'{home_dir}/.pd.db')
            cursor = connection.cursor()
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS incidents (
                pdid INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                state TEXT NOT NULL
            );
            ''')
            connection.commit()
        except Exception as e:
            connection.rollback()
            raise e
        finally:
            if connection:
                connection.close()
    else:
        with open(f'{home_dir}/.pd.db', 'w') as f:
            pass
        init_db()

def insert_incident(pdid ,title, state):
    try:
        connection = sqlite3.connect(f'{home_dir}/.pd.db')
        cursor = connection.cursor()
        query = "INSERT INTO incidents (pdid, title, state) VALUES (?, ?, ?);"
        cursor.execute(query, (pdid, title, state))  #
        connection.commit()
    except Exception as e:
        connection.rollback()
        raise e
    finally:
        if connection:
            connection.close()

def get_incident_by_id(pdid):
    try:
        connection = sqlite3.connect(f'{home_dir}/.pd.db')
        cursor = connection.cursor()
        query = "SELECT * FROM incidents WHERE pdid = ?;"
        cursor.execute(query, (pdid, ))
        result = cursor.fetchone()
        return result
    except Exception as e:
        connection.rollback()
        raise e
    finally:
        if connection:
            connection.close()

   
def get_acknowledged_incidents():
    try:
        connection = sqlite3.connect(f'{home_dir}/.pd.db')
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM incidents WHERE state = 'acknowledged';")
        result = cursor.fetchall()
        return result
    except Exception as e:
        connection.rollback()
        raise e
    finally:
        if connection:
            connection.close()

def delete_incident_by_id(pdid):
    try:
        connection = sqlite3.connect(f'{home_dir}/.pd.db')  # 'example.db' is the database file
        cursor = connection.cursor()
        query = "DELETE FROM incidents WHERE pdid = ?;"
        cursor.execute(query, (pdid, ))
        connection.commit()
    except Exception as e:
        connection.rollback()
        raise e
    finally:
        if connection:
            connection.close()

def show_databases():
    try:
        connection = sqlite3.connect(f'{home_dir}/.pd.db')  # 'example.db' is the database file
        cursor = connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        result = cursor.fetchall()
        return result
    except Exception as e:
        connection.rollback()
        raise e
    finally:
        if connection:
            connection.close()
