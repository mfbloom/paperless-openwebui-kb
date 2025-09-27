FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends     build-essential     ca-certificates     && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt /app
RUN pip install -r requirements.txt

RUN mkdir -p /data

COPY . /app

ENV OUT_DIR=/app/data
ENTRYPOINT ["python", "-u", "main.py"]
