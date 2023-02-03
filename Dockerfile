FROM python:3.8-slim-buster

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY Pipfile.lock ./
COPY Pipfile ./

RUN python -m pip install --upgrade pip
RUN pip install pipenv
RUN pipenv install --deploy --system --ignore-pipfile

COPY innotter .
