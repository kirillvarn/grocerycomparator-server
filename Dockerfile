# syntax=docker/dockerfile:1
FROM python:3
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /code
COPY requirements.txt requirements.txt

RUN apt-get update && apt-get install -y cron

# CRON
ADD cron.py /cron.py
ADD cron.sh /cron.sh
 
RUN chmod +x /cron.py /cron.sh


RUN pip install waitress
RUN pip install -r requirements.txt

COPY . .

# CMD ["FLASK_APP=server.py", "flask", "crontab", "add"]
ENTRYPOINT /cron.sh
CMD ["waitress-serve", "--port=8080", "--threads=16", "--url-scheme=https", "server:app"]
