FROM jupyter/minimal-notebook:python-3.8

COPY ./.docker/jupyter/requirements.txt /tmp/

RUN pip install --no-cache-dir -r /tmp/requirements.txt