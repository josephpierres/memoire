import re
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import requests
import time
from prometheus_client import Counter, Histogram, Gauge, Summary, generate_latest, CONTENT_TYPE_LATEST, make_asgi_app
from starlette.middleware.base import BaseHTTPMiddleware
import uvicorn

app = FastAPI()

# CORS Middleware
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

# Middleware pour les métriques
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

# Requête SQL de base
sqlStatement = "SELECT l.id AS id, l.titre, l.description," \
    " l.isbn, l.annee_apparition, l.image, e.id AS 'editeur.id', e.nom AS 'editeur.nom'," \
    " c.id AS 'categorie.id', c.nom AS 'categorie.nom', a.id AS 'auteur.id', a.nom AS 'auteur.nom'" \
    " FROM livre l LEFT JOIN editeur e ON l.id_editeur = e.id" \
    " LEFT JOIN livrecategorie lc ON l.id = lc.id_livre" \
    " LEFT JOIN categorie c ON lc.id_categorie = c.id" \
    " LEFT JOIN livreauteur la ON l.id = la.id_livre" \
    " LEFT JOIN auteur a ON la.id_auteur = a.id"

# Helper function to query Jolie-proxy and convert the result to a list of dictionaries   
def livre_to_dict(raw_data):
    books_dict = {}

    for entry in raw_data:
        book_id = entry["id"]

        # Vérifier si le livre est déjà ajouté, sinon l'initialiser
        if book_id not in books_dict:
            books_dict[book_id] = {
                "id": entry["id"],
                "titre": entry["titre"],
                "description": entry["description"],
                "isbn": entry["isbn"],
                "annee_apparition": entry["annee_apparition"],
                "image": entry["image"],
                "editeur": {
                    "id": entry["editeur.id"],
                    "nom": entry["editeur.nom"]
                },
                "categories": [],
                "auteurs": []
            }

        # Ajouter les catégories s'il n'est pas encore dans la liste
        categorie = {"id": entry["categorie.id"], "nom": entry["categorie.nom"]}
        if categorie not in books_dict[book_id]["categories"]:
            books_dict[book_id]["categories"].append(categorie)

        # Ajouter les auteurs s'il n'est pas encore dans la liste
        auteur = {"id": entry["auteur.id"], "nom": entry["auteur.nom"]}
        if auteur not in books_dict[book_id]["auteurs"]:
            books_dict[book_id]["auteurs"].append(auteur)

    return list(books_dict.values())

def query_jolie(sql_query):
    try:
        sql_query = sql_query.replace("\n", "")
        response = requests.post(JOLIE_PROXY_URL, json={"query": sql_query})
        response.raise_for_status()
        json_response = response.json()
        rows = json_response.get("result", {}).get("row", [])
        # return [livre_to_dict(row) for row in rows]
        return livre_to_dict(rows)
    except requests.exceptions.RequestException as e:
        EXCEPTIONS.labels(endpoint="Jolie-proxy").inc()
        raise HTTPException(status_code=500, detail=str(e))
    
def query_jolie_all(sql_query):
    try:
        sql_query = sql_query.replace("\n", "")
        response = requests.post(JOLIE_PROXY_URL, json={"query": sql_query})
        response.raise_for_status()
        json_response = response.json()
        if json_response and "result" in json_response and "row" in json_response["result"]:
            return json_response["result"]["row"]
    except requests.exceptions.RequestException as e:
        EXCEPTIONS.labels(endpoint="Jolie-proxy").inc()
        raise HTTPException(status_code=500, detail=str(e))

# ✅ Création dynamique des endpoints sans erreur de paramètre
def create_endpoint(route, sql_modifier=""):    
    @app.get(route)
    def endpoint(request: Request): 
        print(request.base_url)
        match = re.search(r'\{(\w+)\}', route)
        param = match.group(1) if match else None  
        sql_query = sqlStatement + sql_modifier.format(request.path_params.get(param))        
        return query_jolie(sql_query)    

# 
# def create_endpoint(route: str, sql_modifier: str):
#     async def endpoint(request: Request):
#         print(request.base_url)  
#         sql_query = sqlStatement + sql_modifier.format(request.path_params.get(re.search(r'{(.+?)}', route).group(1)))
#         print(sql_query)
#         return query_jolie(sql_query)
#     app.add_api_route(route, endpoint, methods=["GET"])

@app.get('/')
def index():
    return {"biblio-api": "hello, I am ok"}

create_endpoint('/getBookById/{book_id}', " WHERE l.id={}")
create_endpoint('/getBooksByTitle/{search_title}', " WHERE l.titre LIKE '%{}%'")
create_endpoint('/getBooksByAuthor/{search_author}', " WHERE a.nom LIKE '%{}%'")
create_endpoint('/getBooksByCategory/{category_id}', " WHERE c.id = {}")
create_endpoint('/getAllBooks')

@app.get('/getBooksCategories')
def get_books_categories():
    sql_query = "SELECT * FROM categorie;"
    return query_jolie_all(sql_query)

@app.post("/postAllBooks/")
def insert_book(book_data: dict):
    columns = ', '.join(book_data.keys())
    values = ', '.join(f"'{v}'" for v in book_data.values())
    sql_query = f"INSERT INTO livre ({columns}) VALUES ({values});"
    return query_jolie_all(sql_query)

@app.put("/updateBookById/{book_id}")
def update_book(book_id: int, update_data: dict):
    updates = ', '.join(f"{k}='{v}'" for k, v in update_data.items())
    sql_query = f"UPDATE livre SET {updates} WHERE id={book_id};"
    return query_jolie_all(sql_query)

@app.delete("/deleteBook/{book_id}")
def delete_book(book_id: int):
    sql_query = f"DELETE FROM livre WHERE id={book_id};"
    return query_jolie_all(sql_query)


@app.get("/metrics")
async def metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5001)