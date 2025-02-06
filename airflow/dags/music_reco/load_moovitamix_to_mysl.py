import logging
from datetime import datetime, timedelta
from airflow.decorators import dag, task
from utils.mysql_helper import create_users_table, create_tracks_table, create_listen_history, insert_users, insert_tracks, insert_listen_history
from airflow.dags.utils.moovitamix_api_helper import get_voovitamix_users, get_voovitamix_tracks, get_voovitamix_listen_history
import os
import pandas as pd

MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")
#-----------------------------------------
#user tasks
#-----------------------------------------
@task
def extract_users_data():
    try:
        logging.info("Start fetching users data from Voovitamix API.")
        users = get_voovitamix_users()
        logging.info(f"Fetched {len(users)} users.")
        return pd.DataFrame(users)
    except Exception as e:
        logging.error("Error while fetching users data: %s", str(e))
        raise

@task
def transform_user_data(users_df: pd.DataFrame):
    try:
        logging.info("Start cleaning the users data.")
        users_df.loc[users_df['created_at'] > users_df['updated_at'], 'created_at'] = users_df['updated_at']
        logging.info("Finished cleaning the users data.")
        return users_df
    except Exception as e:
        logging.error("Error: %s", str(e))
        raise
@task
def load_user_data(cleaned_users_df: pd.DataFrame):
    try:
        logging.info("Start inserting users in the database.")
        create_users_table(MYSQL_DATABASE)
        insert_users(MYSQL_DATABASE, cleaned_users_df)
        logging.info("Finished inserting the users in the database.")
        return True
    except Exception as e:
        logging.error("Error: %s", str(e))
        raise

#-----------------------------------------
#tracks tasks
#-----------------------------------------
@task
def extract_tracks_data():
    try:
        logging.info("Start fetching tracks data from Voovitamix API.")
        tracks = get_voovitamix_tracks()
        logging.info(f"Fetched {len(tracks)} tracks.")
        return pd.DataFrame(tracks)
    except Exception as e:
        logging.error("Error while fetching tracks data: %s", str(e))
        raise

@task
def transform_tracks_data(tracks_df: pd.DataFrame):
    try:
        logging.info("Start cleaning the tracks data.")
        tracks_df.loc[tracks_df['created_at'] > tracks_df['updated_at'], 'created_at'] = tracks_df['updated_at']
        logging.info("Finished cleaning the users data.")
        return tracks_df
    except Exception as e:
        logging.error("Error: %s", str(e))
        raise
@task
def load_tracks_data(cleaned_tracks_df: pd.DataFrame):
    try:
        logging.info("Start inserting users in the database.")
        create_tracks_table(MYSQL_DATABASE)
        insert_tracks(MYSQL_DATABASE, cleaned_tracks_df)
        logging.info("Finished inserting the users in the database.")
        return True
    except Exception as e:
        logging.error("Error: %s", str(e))
        raise

#-----------------------------------------
#listening history tasks
#-----------------------------------------
@task
def extract_listening_history_data():
    try:
        logging.info("Start fetching listening history data from Voovitamix API.")
        listening_history = get_voovitamix_listen_history()
        logging.info(f"Fetched {len(listening_history)} listening history data.")
        return pd.DataFrame(listening_history)
    except Exception as e:
        logging.error("Error while fetching listening history data: %s", str(e))
        raise

@task
def transform_listening_history_data(listening_history_df: pd.DataFrame):
    try:
        logging.info("Start cleaning the tracks data.")
        exploded_listening_history_df = listening_history_df.explode('items').rename(columns={'items': 'track_id'})
        logging.info("Finished cleaning the users data.")
        return exploded_listening_history_df
    except Exception as e:
        logging.error("Error: %s", str(e))
        raise
@task
def load_listening_histort_data(cleaned_listening_history_df: pd.DataFrame, USERS_LOADED: bool, TRACKS_LOADED: bool):
    try:
        logging.info("Start inserting users in the database.")
        create_listen_history(MYSQL_DATABASE)
        insert_listen_history(MYSQL_DATABASE, cleaned_listening_history_df)
        logging.info("Finished inserting the users in the database.")
        return True
    except Exception as e:
        logging.error("Error: %s", str(e))
        raise



default_args = {
    "owner": "MoovAI",
    "email": ["airflow@example.com"],
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False, 
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

@dag(
    default_args=default_args,
    description="Load data from the Vootamix API to a MySQL database",
    schedule_interval="0 9 * * *",
    start_date=datetime(2025, 2, 6),
    max_active_runs=1,
    tags=["daily", "music_reco"],
)
def etl_vootamix_data():
    users_df = extract_users_data()
    cleaned_users_df = transform_user_data(users_df)
    user_loaded = load_user_data(cleaned_users_df)

    tracks_df = extract_tracks_data()
    cleaned_tracks_df = transform_tracks_data(tracks_df)
    tracks_loaded = load_tracks_data(cleaned_tracks_df)

    listening_history_df = extract_listening_history_data()
    cleaned_listening_history_df = transform_listening_history_data(listening_history_df)
    load_listening_histort_data(cleaned_listening_history_df, user_loaded, tracks_loaded)

dag = etl_vootamix_data()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')