FROM python:latest

ARG APP_NAME=backend.py

WORKDIR /app

COPY requirements.txt requirements.txt
RUN apt-get update
RUN pip install --upgrade pip
# installer les dependances à Python
RUN pip install --no-cache-dir -r requirements.txt 
COPY . .

EXPOSE 5001

CMD python ${APP_NAME}
