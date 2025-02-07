import pytest
from airflow_project.dags.utils.moovitamix_api_helper import get_moovitamix_users, get_moovitamix_tracks, get_moovitamix_listen_history, get_moovitamix_data
from dotenv import load_dotenv
import os

# load_dotenv(".test.env", override=True)
load_dotenv(".test.env", override=True)


def test_get_moovitamix_users():
    users = get_moovitamix_users()
    assert isinstance(users, list)
    assert all(isinstance(user, dict) for user in users)
    assert all(key in users[0] for key in ["id", "first_name", "last_name", "email","gender", "favorite_genres", "created_at", "updated_at"])

def test_get_moovitamix_tracks():
    tracks = get_moovitamix_tracks()
    assert isinstance(tracks, list)
    assert all(isinstance(track, dict) for track in tracks)
    assert all(key in tracks[0] for key in ["id", "name", "artist", "songwriters", "duration", "genres", "album", "created_at", "updated_at"])

def test_get_moovitamix_listen_history():
    listen_history = get_moovitamix_listen_history()
    assert isinstance(listen_history, list)
    assert all(isinstance(history, dict) for history in listen_history)
    assert all(key in listen_history[0] for key in ["user_id", "items", "created_at", "updated_at"])

def test_get_moovitamix_data():
    data = get_moovitamix_data("users")
    assert isinstance(data, list)
    assert all(isinstance(item, dict) for item in data)
    assert all(key in data[0] for key in ["id", "first_name", "last_name", "email","gender", "favorite_genres", "created_at", "updated_at"])

def test_get_moovitamix_data_bad_endpoints():
    data = get_moovitamix_data("user")
    assert isinstance(data, list)
    assert len(data)== 0