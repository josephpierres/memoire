include "console.iol"
include "time.iol"
include "database.iol"
include "jolie-proxy-interface.iol"

// 📌 Service JolieProxy
service JolieProxy {
    execution { concurrent }
    
    // 🔗 Connexion MySQL avec gestion des tentatives
    define initializeMySQLConnection
    {
        scope( connection ) {
            install( ConnectionError =>
                connectionAttempt++;
                if ( connectionAttempt > 3 ) {
                    println@Console("❌ Impossible de se connecter à MySQL après 3 tentatives.")()
                    throw( ConnectionError )
                } else {
                    println@Console("⏳ Tentative " + connectionAttempt + " de connexion à MySQL...")()
                    sleep@Time( connectionAttempt * 1500 )();
                    initializeMySQLConnection

                }
            )
            with( connectionInfo ) {
                .username = "root";
                .port = 3306;
                .password = "password";
                .host = "mysql";
                .database = "gestion_bibliotheque"; 
                .driver = "mysql"
                .checkConnection = 1;
                .toLowerCase = true
            };
            connect@Database( connectionInfo )();
            println@Console("✅ Connexion MySQL établie.")()
            global.mysqlAvailable = true
            
        }
    }

    // 🔗 Connexion HSQLDB Embedded
    define initializeHSQLDBConnection {
        scope( hsqldbConnection ) {
            install( HSQLDBError =>
                println@Console("❌ Impossible de se connecter à HSQLDB.")();
                global.hsqldbAvailable = false
            );
            
            with (connectionInfo) {
                .username = "sa";
                .password = "";
                .host = "";
                .database = "file:bibliodb/bibliodb"; // Pour stockage persistant
                .driver = "hsqldb_embedded"
            };
            connect@Database(connectionInfo)();
            println@Console("✅ Connexion HSQLDB établie.")();
            global.hsqldbAvailable = true
        }
    }



    // ✅ Réception des alertes Prometheus via Alertmanager
    inputPort AlertPort {
        location: "socket://0.0.0.0:9092"
        protocol: http {
            format = "json"
        }
        Interfaces: AlertInterface
    }

    // ✅ Proxy API pour FastAPI
    inputPort ProxyPort {
        location: "socket://0.0.0.0:9091"
        protocol: http {
            format = "json"
        }
        Interfaces: ProxyInterface
    }

    // ✅ Exposition des métriques pour Prometheus
    inputPort MetricsPort {
        location: "socket://0.0.0.0:9191/metrics"
        protocol: http {
            format = "raw"
        }
        Interfaces: ProxyInterface
    }

    // 🔗 Connexion à MySQL et HSQLDB au démarrage
    init {
        // 🔍 Variable globale pour suivre l'état des bases de données
        global.mysqlAvailable = true
        global.hsqldbAvailable = true

        initializeMySQLConnection
;
        initializeHSQLDBConnection
    }

    // ✅ Logique principale
    main {       
        // 🔔 Gestion des alertes de Prometheus
        [ alert(request)() {
            println@Console("🔔 Alerte reçue : " + request.annotations.summary)();
            if (request.status == "firing") {
                if (request.labels.alertname == "MySQL_Down") {
                    global.mysqlAvailable = false;
                    println@Console("🔴 MySQL est hors service. Basculement sur HSQLDB.")()
                }
                if (request.labels.alertname == "MySQL_Up") {
                    global.mysqlAvailable = true;
                    println@Console("✅ MySQL est de retour en ligne.")()
                }
            }
        }] { nullProcess }

        // 📌 Réservation d'un livre
        [ reserveBook(request)(response) {
            if (global.mysqlAvailable) {
                scope(sqlTransaction) {
                    install(SQLException => {
                        response.status = "ERROR";
                        response.error = "Erreur SQL: " + SQLException;
                        println@Console("❌ Erreur lors de l'insertion MySQL: " + SQLException)()
                    });
                    updateRequest = "INSERT INTO Reservations (eventId, userId) VALUES (:eventId, :userId)";
                    updateRequest.eventId = request.eventId;
                    updateRequest.userId = request.userId;
                    update@Database(updateRequest)(dbResponse);
                    response.status = "RESERVED"
                }
            } else if (global.hsqldbAvailable) {
                println@Console("⚠️ MySQL indisponible, basculement sur HSQLDB.")();
                updateRequest = "INSERT INTO Reservations (eventId, userId) VALUES (:eventId, :userId)";
                updateRequest.eventId = request.eventId;
                updateRequest.userId = request.userId;
                update@Database(updateRequest)(dbResponse);
                response.status = "RESERVED (HSQLDB)"
            } else {
                response.status = "ERROR";
                response.error = "Aucune base de données disponible (MySQL et HSQLDB hors ligne)"
            }
        }] { nullProcess }

        // 📌 Récupération des livres
        [ getBooks()(response) {
            if (global.mysqlAvailable) {
                scope(sqlQuery) {
                    install(SQLException => {
                        response.status = "ERROR";
                        response.error = "Erreur SQL: " + SQLException;
                        println@Console("❌ Erreur lors de la récupération des livres MySQL: " + SQLException)()
                    });
                    query@Database("SELECT title FROM books")(sqlResponse);
                    response.books = sqlResponse.result
                }
            } else if (global.hsqldbAvailable) {
                println@Console("⚠️ MySQL indisponible, basculement sur HSQLDB.")();
                query@Database("SELECT title FROM books")(sqlResponse);
                response.books = sqlResponse.result
            } else {
                response.status = "ERROR";
                response.error = "Aucune base de données disponible (MySQL et HSQLDB hors ligne)"
            }
        }] { nullProcess }

        // 📊 Fournir les métriques à Prometheus
        [ metrics()(response) {
            println@Console("📊 Envoi des métriques à Prometheus.")();
            if (global.mysqlAvailable) {
                response.metrics = "mysql_status 1\n"
            } else {
                response.metrics = "mysql_status 0\n"
            }
            
        }] { nullProcess }
    }
}
