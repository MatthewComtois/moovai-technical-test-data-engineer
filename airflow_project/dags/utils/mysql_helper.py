import mysql.connector
import os
import pandas as pd

MYSQL_HOST = os.getenv("MYSQL_HOST", "0.0.0.0")
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "root")


def get_mysql_connection(db_name : str) -> mysql.connector.MySQLConnection:
    return mysql.connector.connect(
        host=MYSQL_HOST,
        port=3306,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=db_name,
    )

def create_users_table(db_name: str):
    connection = get_mysql_connection(db_name)
    mycursor = connection.cursor()
    mycursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT PRIMARY KEY,
            first_name VARCHAR(255),
            last_name VARCHAR(255),
            email VARCHAR(255),
            gender VARCHAR(255),
            favorite_genre VARCHAR(255),
            created_at TIMESTAMP,
            updated_at TIMESTAMP
        )"""
    )
    connection.commit()
    mycursor.close()
    connection.close()

def create_tracks_table(db_name: str):
    connection = get_mysql_connection(db_name)
    mycursor = connection.cursor()
    mycursor.execute("""
        CREATE TABLE IF NOT EXISTS tracks (
            id INT PRIMARY KEY,
            name VARCHAR(255),
            artist VARCHAR(255),
            songwriter VARCHAR(255),
            duration VARCHAR(255),
            album VARCHAR(255),
            genre VARCHAR(255),
            created_at TIMESTAMP,
            updated_at TIMESTAMP
        )"""
    )
    connection.commit()
    mycursor.close()
    connection.close()

def create_listen_history(db_name: str):
    connection = get_mysql_connection(db_name)
    mycursor = connection.cursor()
    mycursor.execute("""
        CREATE TABLE IF NOT EXISTS listen_history (
            user_id INT,
            track_id INT,
            PRIMARY KEY (user_id, track_id),
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (track_id) REFERENCES tracks(id),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )"""
    )
    connection.commit()
    mycursor.close()
    connection.close()

def insert_users(db_name: str, users: pd.DataFrame):
    connection = get_mysql_connection(db_name)
    mycursor = connection.cursor()
    query = """
        INSERT INTO users (id, first_name, last_name, email, gender, favorite_genre, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            first_name = CASE
                WHEN VALUES(updated_at) > updated_at THEN VALUES(first_name)
                ELSE first_name
            END,
            last_name = CASE
                WHEN VALUES(updated_at) > updated_at THEN VALUES(last_name)
                ELSE last_name
            END,
            email=CASE
                WHEN VALUES(updated_at) > updated_at THEN VALUES(email)
                ELSE email
            END,
            gender=CASE
                WHEN VALUES(updated_at) > updated_at THEN VALUES(gender)
                ELSE gender
            END,
            favorite_genre=CASE
                WHEN VALUES(updated_at) > updated_at THEN VALUES(favorite_genre)
                ELSE favorite_genre
            END,
            updated_at=CASE
                WHEN VALUES(updated_at) > updated_at THEN VALUES(updated_at)
                ELSE updated_at
            END;
    """
    users_list = [(row['id'], row["first_name"], row["last_name"], row["email"], row["gender"], row["favorite_genres"], row["created_at"], row["updated_at"]) for _, row in users.iterrows()]
    mycursor.executemany(query, users_list)
    connection.commit()
    mycursor.close()
    connection.close()

def insert_tracks(db_name: str, tracks: pd.DataFrame):
    connection = get_mysql_connection(db_name)
    mycursor = connection.cursor()
    query = """
        INSERT INTO tracks (id, name, artist, songwriter, duration, album, genre, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            name = CASE
                WHEN VALUES(updated_at) > updated_at THEN VALUES(name)
                ELSE name
            END,
            artist = CASE
                WHEN VALUES(updated_at) > updated_at THEN VALUES(artist)
                ELSE artist
            END,
            songwriter=CASE
                WHEN VALUES(updated_at) > updated_at THEN VALUES(songwriter)
                ELSE songwriter
            END,
            duration=CASE
                WHEN VALUES(updated_at) > updated_at THEN VALUES(duration)
                ELSE duration
            END,
            album=CASE
                WHEN VALUES(updated_at) > updated_at THEN VALUES(album)
                ELSE album
            END,
            genre=CASE
                WHEN VALUES(updated_at) > updated_at THEN VALUES(genre)
                ELSE genre
            END,
            updated_at=CASE
                WHEN VALUES(updated_at) > updated_at THEN VALUES(updated_at)
                ELSE updated_at
            END;
    """
    tracks_list = [(row['id'], row["name"], row["artist"], row["songwriters"], row["duration"], row["album"], row["genres"], row["created_at"], row["updated_at"]) for _, row in tracks.iterrows()]
    mycursor.executemany(query, tracks_list)
    connection.commit()
    mycursor.close()
    connection.close()

def insert_listen_history(db_name: str, listen_history: pd.DataFrame):
    connection = get_mysql_connection(db_name)
    mycursor = connection.cursor()
    query = """
        INSERT IGNORE INTO listen_history (user_id, track_id)
        VALUES (%s, %s);
    """
    listen_history_list = [(int(row['user_id']), int(row["track_id"])) for _, row in listen_history.iterrows()]
    mycursor.executemany(query, listen_history_list)
    connection.commit()
    mycursor.close()
    connection.close()


#-----------------------------------------
# Mainly used for testing
#-----------------------------------------
def create_database(db_name: str):
    connection = mysql.connector.connect(
        host=MYSQL_HOST,
        port=3306,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD
    )
    mycursor = connection.cursor()
    mycursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
    connection.commit()
    mycursor.close()
    connection.close()

def delete_database(db_name: str):
    connection = mysql.connector.connect(
        host=MYSQL_HOST,
        port=3306,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD
    )
    mycursor = connection.cursor()
    mycursor.execute(f"DROP DATABASE IF EXISTS {db_name}")
    connection.commit()
    mycursor.close()
    connection.close()