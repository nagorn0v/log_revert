FROM python:3.10.4-slim-buster

WORKDIR /backend

COPY requirements.txt /backend
RUN pip install -r requirements.txt

COPY . /backend

EXPOSE 5000