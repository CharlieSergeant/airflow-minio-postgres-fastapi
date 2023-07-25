from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.empty import EmptyOperator
from include.custom_operators.selenium_operator import SeleniumOperator
from include.scheduler.raw.example_project.example import scrape_example

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 7, 20),  # Adjust the start date according to your requirements
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'selenium_scraping_dag',  # Replace 'selenium_scraping_dag' with your preferred DAG ID
    default_args=default_args,
    description='Scrape data using Selenium',
    schedule_interval=timedelta(days=1),  # Adjust the interval based on your requirements
)

start = EmptyOperator(
    task_id='start',
    dag=dag)

get_scrape = SeleniumOperator(
    task_id='selenium_task',
    script=scrape_example,
    script_args=[],
    dag=dag,
    )

start >> get_scrape
