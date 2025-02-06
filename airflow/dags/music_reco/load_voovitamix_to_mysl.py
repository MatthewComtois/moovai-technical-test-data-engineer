import logging
from datetime import datetime, timedelta
from airflow.decorators import dag, task
from utils.mysql_helper import get_mysql_connection
import os

MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")


@task
def extract_data():
    try:
        logging.info("Test connection to source MySQL database.")
        connection = get_mysql_connection(MYSQL_DATABASE)
        mycursor = connection.cursor()
        logging.info(mycursor.execute("SHOW DATABASES"))  
        logging.info("Test successful.")
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
    extract_data()

dag = etl_vootamix_data()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')