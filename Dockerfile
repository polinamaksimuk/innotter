FROM python:3.10-slim-buster

ENV PYTHONUNBUFFERED=1

RUN pip install "gunicorn==20.0.4"

COPY requirements.txt /
RUN pip install -r requirements.txt

WORKDIR /app

COPY . .

RUN python innotter/manage.py collectstatic --noinput --clear
