
FROM apache/airflow:2.6.3-python3.8
USER root
COPY airflow_data/include/requirements.txt .
RUN pip3 install --user --no-cache-dir -r requirements.txt

RUN groupadd --gid 999 docker \
   && usermod -aG docker airflow

RUN mkdir downloads

ENV PYTHONPATH=/home/airflow/.local/lib/python3.8/site-packages:/opt/airflow/include:/opt/airflow