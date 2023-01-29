# syntax=docker/dockerfile:1
FROM python:3
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /code
COPY requirements.txt requirements.txt

# CRON
COPY cronjob /etc/cron.d/hello-cron
RUN crontab /etc/cron.d/hello-cron
COPY cron.sh /usr/local/bin/cron.sh
RUN chmod 0777 /usr/local/bin/cron.sh

RUN pip install waitress
RUN pip install -r requirements.txt
COPY . .

# CMD ["FLASK_APP=server.py", "flask", "crontab", "add"]
ENTRYPOINT ["cron.sh"]
CMD ["waitress-serve", "--port=8080", "--threads=16", "--url-scheme=https", "server:app"]
