include "console.iol"
include "http.iol"
include "json.iol"

// Définition des interfaces
interface PythonInterface {
    RequestResponse:
        reserveBook(BookRequest)(BookResponse),
        getBooks(void)(BookListResponse)
}

interface MySQLInterface {
    RequestResponse:
        executeQuery(DatabaseRequest)(DatabaseResponse)
}

interface RedisInterface {
    RequestResponse:
        reserveBook(BookRequest)(BookResponse),
        getBooks(void)(BookListResponse)
}

interface PrometheusInterface {
    RequestResponse:
        fetchMetrics(QueryRequest)(MetricsResponse)
}

// Définition des types
type BookRequest {
    eventId: string
    userId: string
}

type BookResponse {
    BookId: string
    status: string
    error?: string
}

type BookListResponse {
    Books: any
}

type DatabaseRequest {
    query: string
    params?: any
}

type DatabaseResponse {
    result?: any
    error?: string
    status: string
}

type QueryRequest {
    query: string
}

type MetricsResponse {
    data: any
}