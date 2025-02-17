include "console.iol"
include "http.iol"
include "json.iol"

interface ProxyInterface {
    RequestResponse:
        reserveBook(BookRequest)(BookResponse),
        getBooks(void)(BookListResponse),
        getMetrics(void)(MetricsResponse)
}

interface DatabaseInterface {
    RequestResponse:
        executeQuery(DatabaseRequest)(DatabaseResponse)
}

interface AlertInterface {
    RequestResponse:
        alert(AlertRequest)(void)
}

// Définition des types
type BookRequest {
    eventId: string
    userId: string
}

type BookResponse {
    bookId: string
    status: string
    error?: string
}

type BookListResponse {
    books: list<string>
}

type DatabaseRequest {
    query: string
    params?: list<string>
}

type DatabaseResponse {
    result?: any
    error?: string
    status: string
}

type AlertRequest {
    status: string
    labels: {
        alertname: string
    }
    annotations: {
        summary: string
        description: string
    }
}

type MetricsResponse {
    metrics: string
}
