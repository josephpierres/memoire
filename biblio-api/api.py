from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import requests
import time
from prometheus_client import Counter, Histogram, Gauge, Summary, generate_latest, CONTENT_TYPE_LATEST, make_asgi_app
from starlette.middleware.base import BaseHTTPMiddleware
import uvicorn
import re
from starlette.routing import Mount

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

JOLIE_PROXY_URL = "http://jolie-proxy:9091/executeQuery"

# Prometheus Metrics
REQUESTS = Counter('biblio_api_requests_total', 'Total requests', ["method", "endpoint"])
RESPONSES = Counter('biblio_api_responses_total', 'Total responses', ["method", "endpoint", "http_status"])
EXCEPTIONS = Counter('biblio_api_exceptions_total', 'Total exceptions', ["endpoint"])
REQUESTS_PROCESSING_TIME = Histogram('biblio_api_requests_duration_seconds', 'Request duration', ["method", "endpoint"])
REQUESTS_IN_PROGRESS = Gauge('biblio_api_requests_in_progress', 'Requests in progress')
REQUEST_TIME = Summary('biblio_api_request_processing_seconds', 'Request processing time')

class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        method = request.method
        endpoint = request.url.path
        REQUESTS.labels(method=method, endpoint=endpoint).inc()
        REQUESTS_IN_PROGRESS.inc()

        start_time = time.time()
        try:
            response = await call_next(request)
            duration = time.time() - start_time
            REQUESTS_PROCESSING_TIME.labels(method=method, endpoint=endpoint).observe(duration)
            REQUEST_TIME.observe(duration)
            RESPONSES.labels(method=method, endpoint=endpoint, http_status=str(response.status_code)).inc()
            return response
        except Exception as e:
            EXCEPTIONS.labels(endpoint=endpoint).inc()
            raise e
        finally:
            REQUESTS_IN_PROGRESS.dec()

app.add_middleware(MetricsMiddleware)
route = Mount("/metrics", make_asgi_app())
route.path_regex = re.compile('^/metrics(?P<path>.*)$')
app.routes.append(route)

def query_jolie(sql_query):
    try:
        response = requests.post(JOLIE_PROXY_URL, json={"query": sql_query})
        response.raise_for_status()
        result = response.json().get("result").get("row")
        return response.json().get("result").get("row")
    except requests.exceptions.RequestException as e:
        EXCEPTIONS.labels(endpoint="Jolie-proxy").inc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get('/')
def index():
    print(f" hello from { __name__ }, I am ok")   
    return { "biblio-api": f" hello from { __name__ }, I am ok" }

@app.get("/books/{book_id}")
def get_book_by_id(book_id: int):
    sql_query = f"SELECT * FROM livre WHERE id={book_id};"
    return query_jolie(sql_query)

@app.get("/books/title/{search_title}")
def get_books_by_title(search_title: str):
    sql_query = f"SELECT * FROM livre WHERE titre LIKE '%{search_title}%';"
    return query_jolie(sql_query)

@app.get("/books/author/{search_author}")
def get_books_by_author(search_author: str):
    sql_query = f"""
    SELECT livre.* FROM livre
    JOIN livreauteur ON livre.id = livreauteur.id_livre
    JOIN auteur ON livreauteur.id_auteur = auteur.id
    WHERE auteur.nom LIKE '%{search_author}%';
    """
    return query_jolie(sql_query)

@app.get("/books/")
def get_all_books():
    sql_query = "SELECT * FROM livre;"
    return query_jolie(sql_query)

@app.get("/books/category/{category_id}")
def get_books_by_category(category_id: int):
    sql_query = f"""
    SELECT livre.* FROM livre
    JOIN livrecategorie ON livre.id = livrecategorie.id_livre
    WHERE livrecategorie.id_categorie = {category_id};
    """
    return query_jolie(sql_query)

@app.post("/books/")
def insert_book(book_data: dict):
    columns = ', '.join(book_data.keys())
    values = ', '.join(f"'{v}'" for v in book_data.values())
    sql_query = f"INSERT INTO livre ({columns}) VALUES ({values});"
    return query_jolie(sql_query)

@app.put("/books/{book_id}")
def update_book(book_id: int, update_data: dict):
    updates = ', '.join(f"{k}='{v}'" for k, v in update_data.items())
    sql_query = f"UPDATE livre SET {updates} WHERE id={book_id};"
    return query_jolie(sql_query)

@app.delete("/books/{book_id}")
def delete_book(book_id: int):
    sql_query = f"DELETE FROM livre WHERE id={book_id};"
    return query_jolie(sql_query)

@app.get("/metrics")
def metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5001)
