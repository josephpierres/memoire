FROM python:latest

# ARG APP_NAME=backend.py
ARG APP_NAME=main.py

WORKDIR /app

COPY requirements.txt requirements.txt
RUN apt-get update
RUN pip install --upgrade pip
# installer les dependances à Python
RUN pip install --no-cache-dir -r requirements.txt 
COPY . .

EXPOSE 5001

# Lancer l'application FastAPI avec Uvicorn
# CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5001"]
# ou avec flask
CMD python ${APP_NAME}
