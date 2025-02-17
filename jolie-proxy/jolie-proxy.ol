include "console.iol"
include "http.iol"
include "json.iol"
include "interface.iol"

// Variable globale pour l'état de MySQL
global {
    bool mysqlAvailable = true
}

// Génération des métriques Prometheus
define generateMetrics()(response) {
    if (global.mysqlAvailable) {
        response.metrics = "redis_status 1\n"
    } else {
        response.metrics = "redis_status 2\n"
    }
}

// Gérer les réservations en fonction de l'état de MySQL
define handleReservation(request)(response) {
    if (global.mysqlAvailable) {
        databaseRequest.query = "INSERT INTO Books (ISBN, user_id) VALUES (?, ?)"
        databaseRequest.params = [request.eventId, request.userId]
        executeQuery@MySQLPort(databaseRequest)(databaseResponse)
    } else {
        reserveBook@RedisPort(request)(databaseResponse)
    }
    response << databaseResponse
}

// Récupérer la liste des livres depuis MySQL ou Redis
define getBooksFromDatabase()(response) {
    if (global.mysqlAvailable) {
        databaseRequest.query = "SELECT * FROM Books"
        executeQuery@MySQLPort(databaseRequest)(databaseResponse)
    } else {
        getBooks@RedisPort()(databaseResponse)
    }
    response << databaseResponse
}

// Service JolieProxy
service JolieProxy {
    execution { concurrent }

    // Réception des alertes Prometheus via Alertmanager
    inputPort AlertPort {
        location: "http://0.0.0.0:9092"
        protocol: http {
            format = "json"
        }
        Interfaces: AlertInterface
    }

    // Proxy API pour Biblio-API
    inputPort ProxyPort {
        location: "socket://0.0.0.0:9091"
        protocol: http {
            format = "json"
        }
        Interfaces: ProxyInterface
    }

    // Exposition des métriques pour Prometheus
    inputPort MetricsPort {
        location: "http://0.0.0.0:9100/metrics"
        protocol: http {
            format = "plain"
        }
        Interfaces: ProxyInterface
    }

    // Connexion MySQL
    outputPort MySQLPort {
        location: "socket://mysql:3306"
        protocol: http {
            format = "json"
        }
        Interfaces: DatabaseInterface
    }

    // Connexion Redis
    outputPort RedisPort {
        location: "socket://redis:6379"
        protocol: http {
            format = "json"
        }
        Interfaces: ProxyInterface
    }

    // Logique principale
    main {
        // Réception d'une alerte depuis Alertmanager
        [ alert(request) {
            println@Console("🔔 Alerte reçue : " + request.annotations.summary)

            if (request.status == "firing") {
                if (request.labels.alertname == "MySQL_Down") {
                    global.mysqlAvailable = false
                    println@Console("🔴 MySQL est hors service. Redirection vers Redis.")()
                }
                if (request.labels.alertname == "MySQL_Up") {
                    global.mysqlAvailable = true
                    println@Console("✅ MySQL est de retour en ligne. Reconnexion.")()
                }
            }
        }]

        // Réservation d'un livre
        [ reserveBook(request)(response) {
            scope(requestHandling) {
                install(Error => {
                    response.error = "Erreur traitement : " + Error
                    response.status = "ERROR"
                })
                handleReservation(request)(response)
            }
        }]

        // Récupération des livres
        [ getBooks()(response) {
            scope(requestHandling) {
                install(Error => {
                    response.error = "Erreur traitement : " + Error
                    response.status = "ERROR"
                })
                getBooksFromDatabase()(response)
            }
        }]

        // Fournir les métriques à Prometheus
        [ getMetrics()(response) {
            generateMetrics()(response)
        }]
    }
}
