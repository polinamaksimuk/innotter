FROM python:3.10-slim-buster

ENV PYTHONUNBUFFERED=1

RUN pip install "gunicorn==20.0.4"

COPY requirements.txt /
RUN pip install -r requirements.txt

WORKDIR /app

COPY innotter .

RUN python manage.py collectstatic --noinput --clear
