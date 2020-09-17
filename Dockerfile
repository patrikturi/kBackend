FROM python:3.8.5-slim

WORKDIR /kbackend

COPY ./requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

COPY ./kbackend .

COPY ./kbackend/app_entrypoint.sh /app_entrypoint.sh
RUN chmod +x /app_entrypoint.sh
RUN chmod +x manage.py
