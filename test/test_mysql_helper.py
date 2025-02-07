import pytest
from airflow_project.dags.utils.mysql_helper import *
from fastapi_app.src.moovitamix_fastapi.classes_out import TracksOut, UsersOut, ListenHistoryOut, gender_list, genre_list
from dotenv import load_dotenv
import os
import pandas as pd


load_dotenv(".test.env", override=True)


@pytest.fixture
def setup_database():
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "test_db")
    create_database(MYSQL_DATABASE)

    yield  MYSQL_DATABASE
    
    delete_database(MYSQL_DATABASE)

def create_users_df(nb_user):
    users = []
    for i in range(nb_user):
        user = UsersOut.generate_fake()    
        users.append(
            {
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "gender": user.gender,
                "favorite_genres": user.favorite_genres,
                "created_at": user.created_at,
                "updated_at": user.updated_at
            }
        )
    return pd.DataFrame(users)

def create_tracks_df(nb_tracks):
    tracks = []
    for i in range(nb_tracks):
        track = TracksOut.generate_fake()    
        tracks.append(
            {
                "id": track.id,
                "name": track.name,
                "artist": track.artist,
                "songwriters": track.songwriters,
                "duration": track.duration,
                "album": track.album,
                "genres": track.genres,
                "created_at": track.created_at,
                "updated_at": track.updated_at
            }
        )
    return pd.DataFrame(tracks)


def test_create_delete_database():
    MYSQL_DATABASE = "test_db"
    create_database(MYSQL_DATABASE)
    conn = get_mysql_connection(MYSQL_DATABASE)
    conn.close()
    delete_database(MYSQL_DATABASE)
    with pytest.raises(Exception):
        get_mysql_connection(MYSQL_DATABASE)

def test_get_mysql_connection(setup_database):
    conn = get_mysql_connection(setup_database)
    assert conn.is_connected()
    conn.close()
    assert not conn.is_connected()

def test_get_mysql_connection_bad_db():
    with pytest.raises(Exception):
        get_mysql_connection("BAD_DB")

def test_create_users_table(setup_database):
    create_users_table(setup_database)
    conn = get_mysql_connection(setup_database)
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        assert len(tables) == 1
        assert tables[0]["Tables_in_test_db"] == "users"
        cursor.execute("DESCRIBE users")
        columns = cursor.fetchall()
        assert len(columns) == 8
        assert columns[0]["Field"] == "id"
        assert columns[0]["Type"] == b"int"
        assert columns[0]["Key"] == "PRI"
        assert columns[1]["Field"] == "first_name"
        assert columns[1]["Type"] == b"varchar(255)"
        assert columns[2]["Field"] == "last_name"
        assert columns[2]["Type"] == b"varchar(255)"
        assert columns[3]["Field"] == "email"
        assert columns[3]["Type"] == b"varchar(255)"
        assert columns[4]["Field"] == "gender"
        assert columns[4]["Type"] == b"varchar(255)"
        assert columns[5]["Field"] == "favorite_genre"
        assert columns[5]["Type"] == b"varchar(255)"
        assert columns[6]["Field"] == "created_at"
        assert columns[6]["Type"] == b"timestamp"
        assert columns[7]["Field"] == "updated_at"
        assert columns[7]["Type"] == b"timestamp"
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def test_create_tracks_table(setup_database):
    create_tracks_table(setup_database)
    conn = get_mysql_connection(setup_database)
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        assert len(tables) == 1
        assert tables[0]["Tables_in_test_db"] == "tracks"
        cursor.execute("DESCRIBE tracks")
        columns = cursor.fetchall()
        assert len(columns) == 9
        assert columns[0]["Field"] == "id"
        assert columns[0]["Type"] == b"int"
        assert columns[0]["Key"] == "PRI"
        assert columns[1]["Field"] == "name"
        assert columns[1]["Type"] == b"varchar(255)"
        assert columns[2]["Field"] == "artist"
        assert columns[2]["Type"] == b"varchar(255)"
        assert columns[3]["Field"] == "songwriter"
        assert columns[3]["Type"] == b"varchar(255)"
        assert columns[4]["Field"] == "duration"
        assert columns[4]["Type"] == b"varchar(255)"
        assert columns[5]["Field"] == "album"
        assert columns[5]["Type"] == b"varchar(255)"
        assert columns[6]["Field"] == "genre"
        assert columns[6]["Type"] == b"varchar(255)"
        assert columns[7]["Field"] == "created_at"
        assert columns[7]["Type"] == b"timestamp"
        assert columns[8]["Field"] == "updated_at"
        assert columns[8]["Type"] == b"timestamp"
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def test_create_listen_history_table(setup_database):
    create_users_table(setup_database)
    create_tracks_table(setup_database)
    create_listen_history(setup_database)
    conn = get_mysql_connection(setup_database)
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        assert len(tables) == 3
        assert tables[0]["Tables_in_test_db"] == "listen_history"
        cursor.execute("DESCRIBE listen_history")
        columns = cursor.fetchall()
        assert len(columns) == 3
        assert columns[0]["Field"] == "user_id"
        assert columns[0]["Type"] == b"int"
        assert columns[0]["Key"] == "PRI"
        assert columns[1]["Field"] == "track_id"
        assert columns[1]["Type"] == b"int"
        assert columns[1]["Key"] == "PRI"
        assert columns[2]["Field"] == "created_at"
        assert columns[2]["Type"] == b"timestamp"
        cursor.execute("SHOW CREATE TABLE listen_history")
        create_table = cursor.fetchall()[0]["Create Table"]
        assert "FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)" in create_table
        assert "FOREIGN KEY (`track_id`) REFERENCES `tracks` (`id`)" in create_table
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def test_insert_users(setup_database):
    nb_user = 2
    conn = None
    cursor = None
    users_df = create_users_df(nb_user)
    try:
        create_users_table(setup_database)
        insert_users(setup_database,users_df)

        conn = get_mysql_connection(setup_database)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users")
        results = cursor.fetchall()
        assert len(results) == nb_user
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def test_insert_tracks(setup_database):
    nb_tracks = 2
    conn = None
    cursor = None

    tracks_df = create_tracks_df(nb_tracks)
    try:
        create_tracks_table(setup_database)
        insert_tracks(setup_database,tracks_df)

        conn = get_mysql_connection(setup_database)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM tracks")
        results = cursor.fetchall()
        assert len(results) == nb_tracks
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def test_insert_listen_history(setup_database):
    conn = None
    cursor = None
    nb_user = 2
    nb_tracks = 2
    users_df = create_users_df(nb_user)
    tracks_df = create_tracks_df(nb_tracks)

    listen_history = []
    for i in range(nb_user):
        for j in range(nb_tracks):
            listen_history.append(
                {
                    "user_id": users_df["id"][i],
                    "track_id": tracks_df["id"][j]
                }
            )
    
 
    listen_history_df = pd.DataFrame(listen_history)
    
    try:
        create_users_table(setup_database)
        create_tracks_table(setup_database)
        create_listen_history(setup_database)

        insert_users(setup_database,users_df)
        insert_tracks(setup_database,tracks_df)
        insert_listen_history(setup_database,listen_history_df)

        conn = get_mysql_connection(setup_database)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM listen_history")
        results = cursor.fetchall()
        assert len(results) == nb_user * nb_tracks
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

