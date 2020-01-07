import logging
import sqlite3
from sqlite3 import Error

logging.getLogger(__name__)


DB_NAME = "smog_db.sqlite3"

TABLE_NAME = "smog_stats"

SQL_CREATE_TABLE = f""" 
    CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
        id integer PRIMARY KEY,
        pm10 real NOT NULL,
        pm25 real NOT NULL,
        datetime text NOT NULL
    ); """

SQL_INSERT = f"INSERT INTO {TABLE_NAME}(pm10, pm25, datetime) VALUES(?,?,?);"


def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        logging.error(e)

    return conn


def create_table(conn, create_table_sql):
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        logging.error(e)


def insert_row(conn, row):
    try:
        cursor = conn.cursor()
        cursor.execute(SQL_INSERT, row)
    except Error as e:
        logging.error(e)
    else:
        conn.commit()
        return cursor.lastrowid
    return None


def initialize_db():
    conn = create_connection(DB_NAME)
    if conn is not None:
        create_table(conn, SQL_CREATE_TABLE)
    else:
        logging.error(f"DB [{DB_NAME}]: cannot create the database connection!")


if __name__ == '__main__':
    initialize_db()
