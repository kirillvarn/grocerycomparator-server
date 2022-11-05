# syntax=docker/dockerfile:1
FROM python:3
ARG PORT
ENV port=$port
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /code
COPY requirements.txt requirements.txt
RUN pip install waitress
RUN pip install -r requirements.txt
COPY . .
CMD ["waitress-serve", "--port=${port}", "--threads=16", "--url-scheme=https", "server:app"]
