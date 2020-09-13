FROM python:3.8.5-slim

WORKDIR /kbackend

COPY ./kbackend .

RUN pip install -r requirements.txt

COPY ./kbackend/app_entrypoint.sh /app_entrypoint.sh
RUN chmod +x /app_entrypoint.sh
RUN chmod +x manage.py
