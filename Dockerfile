# syntax=docker/dockerfile:1
FROM python:3
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /code
COPY requirements.txt requirements.txt

RUN apt-get update && apt-get install -y cron

# CRON
COPY cronjob /etc/cron.d/cronjob
RUN crontab /etc/cron.d/cronjob
 
COPY launch.sh /usr/local/bin/launch.sh
RUN chmod 0777 /usr/local/bin/launch.sh

RUN pip install waitress
RUN pip install -r requirements.txt

COPY . .

# CMD ["FLASK_APP=server.py", "flask", "crontab", "add"]
ENTRYPOINT ["launch.sh"]
CMD ["waitress-serve", "--port=8080", "--threads=16", "--url-scheme=https", "server:app"]