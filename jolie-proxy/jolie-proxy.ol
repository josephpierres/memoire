include "console.iol"
include "http.iol"
include "json.iol"
include "time.iol"
include "jolie-proxy-interface.iol"
include "jolie-proxy-port.iol"

// Variables globales
global {
    bool mysqlAvailable = true
}


// Définition des interfaces



// Fonction pour vérifier l'état de MySQL via Prometheus
define checkMySQLStatus {
    scope(prometheusCheck) {
        install(Error => {
            println@Console("Error checking MySQL status: " + Error)()
            global.mysqlAvailable = false
        })

        queryRequest.query = "up{service=\"mysql\"}"
        fetchMetrics@PrometheusAPI(queryRequest)(metricsResponse)

        if (#metricsResponse.data.result > 0 && metricsResponse.data.result[0].value[1] == "1") {
            global.mysqlAvailable = true
            println@Console("MySQL is available.")()
        } else {
            global.mysqlAvailable = false
            println@Console("MySQL is unavailable. Redirecting to Redis.")()
        }
    }
}

// Fonction pour réserver un livre dans MySQL
define reserveBookInMySQL(request)(response) {
    query = "INSERT INTO Books (ISBN, user_id) VALUES (?, ?)"
    params = [request.eventId, request.userId]
    databaseRequest.query = query
    databaseRequest.params = params
    executeQuery@MySQLPort(databaseRequest)(databaseResponse)
    response << databaseResponse
}

// Fonction pour récupérer les livres depuis MySQL
define getBooksFromMySQL()(response) {
    query = "SELECT * FROM Books"
    databaseRequest.query = query
    executeQuery@MySQLPort(databaseRequest)(databaseResponse)
    response << databaseResponse
}

// Fonction principale pour gérer les réservations
define handleReservation(request)(response) {
    if (global.mysqlAvailable) {
        // Utiliser MySQL
        reserveBookInMySQL(request)(response)
    } else {
        // Utiliser Redis
        reserveBook@RedisPort(request)(response)
    }
}

// Surveillance continue de MySQL
define monitorMySQL {
    while (true) {
        checkMySQLStatus()
        sleep@Time(10000)()  // Vérifier toutes les 10 secondes
    }
}

// Logique principale
main {
    // Démarrer la surveillance de MySQL dans un thread séparé
    spawn monitorMySQL()

    // Traitement des requêtes
    [ reserveBook(request)(response) {
        scope(requestHandling) {
            install(Error => {
                response.error = "Request handling error: " + Error
                response.status = "ERROR"
            })

            handleReservation(request)(response)
        }
    } ]

    [ getBooks()(response) {
        scope(requestHandling) {
            install(Error => {
                response.error = "Request handling error: " + Error
                response.status = "ERROR"
            })

            if (global.mysqlAvailable) {
                getBooksFromMySQL()(response)
            } else {
                getBooks@RedisPort()(response)
            }
        }
    } ]
}