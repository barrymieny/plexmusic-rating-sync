# syntax=docker/dockerfile:1

FROM python:3.12.0a3-slim-bullseye
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .
CMD ["python", "./sync-plex-music-ratings.py"]
