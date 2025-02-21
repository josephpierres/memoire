from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import requests
import time
from prometheus_client import Counter, Histogram, Gauge, Summary, generate_latest, CONTENT_TYPE_LATEST
from starlette.middleware.base import BaseHTTPMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Flask Front-end origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# URL du proxy Jolie
RESERVE_BOOK_URL = "http://jolie-proxy:9091/reserveBook"
GET_BOOKS_URL = "http://jolie-proxy:9091/getBooks"

# Define Prometheus metrics
REQUESTS = Counter('biblio_api_requests_total', 'Total number of requests received', ["method", "endpoint"])
RESPONSES = Counter('biblio_api_responses_total', 'Total number of responses sent', ["method", "endpoint", "http_status"])
EXCEPTIONS = Counter('biblio_api_exceptions_total', 'Total number of exceptions encountered', ["endpoint"])
REQUESTS_PROCESSING_TIME = Histogram('biblio_api_requests_duration_seconds', 'Time taken to process requests', ["method", "endpoint"])
REQUESTS_IN_PROGRESS = Gauge('biblio_api_requests_in_progress', 'Number of requests in progress')
REQUEST_TIME = Summary('biblio_api_request_processing_seconds', 'Time spent processing requests')

# Middleware pour capturer les métriques sur toutes les requêtes
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

# Endpoint pour réserver un book
@app.post("/reserveBook")
async def reserve_book(data: dict):
    event_id = data.get("eventId")
    user_id = data.get("userId")

    if not event_id or not user_id:
        RESPONSES.labels(method="POST", endpoint="/reserveBook", http_status="400").inc()
        raise HTTPException(status_code=400, detail="eventId and userId are required")
    
    try:
        response = requests.post(RESERVE_BOOK_URL, json={"eventId": event_id, "userId": user_id})
        RESPONSES.labels(method="POST", endpoint="/reserveBook", http_status=str(response.status_code)).inc()
        return response.json()
    except Exception as e:
        EXCEPTIONS.labels(endpoint="/reserveBook").inc()
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint pour récupérer la liste des books
@app.get("/getBooks")
async def get_books():
    try:
        response = requests.get(GET_BOOKS_URL)
        RESPONSES.labels(method="GET", endpoint="/getBooks", http_status=str(response.status_code)).inc()
        return response.json()
    except Exception as e:
        EXCEPTIONS.labels(endpoint="/getBooks").inc()
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint pour exposer les métriques Prometheus
@app.get("/metrics")
async def metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

# Lancer l'application avec Uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5001)
