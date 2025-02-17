include "console.iol"
include "time.iol"
include "string_utils.iol"
include "json_utils.iol"

interface AdaptationInterface {
    RequestResponse:
        monitorScaling(void)(string),
        getMetrics(void)(MetricsResponse),
        adjustScaling(ScalingRequest)(string)
}

interface PrometheusInterface {
    RequestResponse:
        getMetrics(string)(string)
}

interface KedaInterface {
    RequestResponse:
        adjustScaling(ScalingRequest)(string)
}

type MetricsResponse {
    cpu: double
    memory: double
    requestRate: double
    responseTime: double
    .frontend: void {
        replicas: int
        load: double
    }
    .backend: void {
        replicas: int
        load: double
    }
}

type ScalingRequest {
    service: string
    action: string    // "up", "down", or specific replica count
    reason: string
}

service AdaptationService {
    execution: concurrent

    inputPort AdaptationPort {
        Location: "socket://0.0.0.0:8088"
        Protocol: http {
            format = "json"
            .statusCode -> statusCode
        }
        Interfaces: AdaptationInterface
    }

    outputPort PrometheusAPI {
        Location: "socket://bibliobservability-kube-pr-prometheus.monitoring.svc.cluster.local:9090"
        Protocol: http {
            format = "json"
            .osc.getMetrics.alias = "/api/v1/query"
            .osc.getMetrics.method = "get"
        }
        Interfaces: PrometheusInterface
    }

    outputPort KedaAPI {
        Location: "socket://keda-operator.keda.svc.cluster.local:9666"
        Protocol: http {
            format = "json"
            .osc.adjustScaling.alias = "/scale"
            .osc.adjustScaling.method = "post"
        }
        Interfaces: KedaInterface
    }

    init {
        println@Console("Jolie Adaptation Service Started")()
    }

    main {
        [ monitorScaling()( response ) {
            scope( monitoring ) {
                install( Error => 
                    response = "Error: " + monitoring.Error
                )

                // Récupérer les métriques de Prometheus
                getMetrics@PrometheusAPI("query=up")( metrics )

                if ( metrics.frontend.load > 75.0 ) {
                    // Déclencher le scaling via KEDA pour le frontend
                    scaleRequest.service = "nginx"
                    scaleRequest.action = "up"
                    scaleRequest.reason = "High load detected: " + string(metrics.frontend.load)
                    adjustScaling@KedaAPI(scaleRequest)(scaleResponse)
                    response = "Scaling up frontend: " + scaleResponse
                } 
                else if ( metrics.backend.responseTime > 2.0 && metrics.backend.replicas < 2 ) {
                    // Déclencher le scaling pour le backend
                    scaleRequest.service = "biblio-api"
                    scaleRequest.action = "up"
                    scaleRequest.reason = "High response time detected: " + string(metrics.backend.responseTime)
                    adjustScaling@KedaAPI(scaleRequest)(scaleResponse)
                    response = "Scaling up backend to max replicas: " + scaleResponse
                } 
                else if ( metrics.backend.responseTime <= 1.0 && metrics.backend.replicas > 0 ) {
                    // Réduire les réplicas pour le backend si la charge est faible
                    scaleRequest.service = "biblio-api"
                    scaleRequest.action = "down"
                    scaleRequest.reason = "Low response time detected, reducing replicas."
                    adjustScaling@KedaAPI(scaleRequest)(scaleResponse)
                    response = "Scaling down backend: " + scaleResponse
                } else {
                    response = "No scaling action required."
                }

                println@Console("Adaptation Decision: " + response)()
            }
        } ]
    }
}
