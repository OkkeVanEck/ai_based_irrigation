FROM python:3.9.6-slim-buster

ARG pg_host
ARG pg_username
ARG pg_password

ENV POSTGRES_HOST=$pg_host
ENV POSTGRES_USERNAME=$pg_username
ENV POSTGRES_PASSWORD=$pg_password

RUN apt-get update && apt-get install -y gcc build-essential

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

ENV TZ=Europe/Amsterdam
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

WORKDIR /app

COPY . .

EXPOSE 5555
CMD python irr_api.py
