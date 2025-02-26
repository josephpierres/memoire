# Ce projet est compos'e de plusieurs services:
## Services inclus
- fastapi-biblio : API FastAPI pour la gestion des livres et métriques Prometheus.
- jolie-proxy : Service Jolie pour la logique métier.
- mysql : Base de données pour stocker les informations.
- hsqldb_embeded : Cache pour améliorer les performances.
- app : Frontend pour l'application (si tu as une interface utilisateur).
- prometheus : Collecte des métriques des services.
- mysql-exporter : Expose les métriques MySQL pour Prometheus.
- grafana : Visualisation des métriques.
- keda : Auto-scaling basé sur les métriques.
- 
## lancement des installations
kubectl create namespace bbl
kubectl -n bbl create sc-mysql.yaml
kubectl -n bbl create pv-mysql.yaml
helm install -n bbl jolie-proxy ./jolie-proxy
helm install -n bbl mysql ./mysql
helm install -n bbl biblio-api ./biblio_api
helm install -n bbl biblio-app ./biblio_app
helm install -n bbl nginx ./nginx

## installation de kube-prometheus-stack pour le monitoring
helm repo add stable https://charts.helm.sh/stable
kubectl create namespace monitoring
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm install bibliobservability prometheus-community/kube-prometheus-stack --namespace monitoring 
helm upgrade --install bibliobservability prometheus-community/kube-prometheus-stack \
  --namespace monitoring --values prometheus/prom-values.yaml 
kubectl apply -f prometheus/mysql-alerts.yaml -n monitoring

## Installation de KEDA pour l'autoscaling
helm repo add kedacore https://kedacore.github.io/charts
kubectl create namespace keda
helm install keda kedacore/keda --namespace keda
kubectl apply -f keda/biblio-api-so.yaml