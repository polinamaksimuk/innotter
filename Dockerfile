FROM python:3.10-slim-buster

ENV PYTHONUNBUFFERED=1

COPY Pipfile Pipfile.lock ./
RUN python -m pip install --upgrade pip
RUN pip install pipenv && pipenv install --dev --system --deploy

WORKDIR /app

COPY innotter .

RUN python manage.py collectstatic --noinput --clear
