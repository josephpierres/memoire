# Ce projet est compos'e de plusieurs services:
## Services inclus
- fastapi-biblio : API FastAPI pour la gestion des livres et métriques Prometheus.
- jolie-proxy : Service Jolie pour la logique métier.
- mysql : Base de données pour stocker les informations.
- redis : Cache pour améliorer les performances.
- app : Frontend pour l'application (si tu as une interface utilisateur).
- prometheus : Collecte des métriques des services.
- mysql-exporter : Expose les métriques MySQL pour Prometheus.
- grafana : Visualisation des métriques.
- keda : Auto-scaling basé sur les métriques.
- 
## lancement des installations
kubectl -n bbl apply -k . 
helm install -n bbl jolie-proxy ./jolie-proxy
helm install -n bbl mysql ./mysql
helm install -n bbl redis ./redis
helm install -n bbl biblio-api ./biblio_api
helm install -n bbl biblio-app ./biblio_app
helm install -n bbl nginx ./nginx

helm repo add stable https://charts.helm.sh/stable
kubectl create namespace monitoring

helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

helm install bibliobservability prometheus-community/kube-prometheus-stack --namespace monitoring 

helm upgrade --install bibliobservability prometheus-community/kube-prometheus-stack \
  --namespace monitoring --values prometheus/prom-values.yaml 

helm repo add kedacore https://kedacore.github.io/charts


kubectl create namespace keda
helm install keda kedacore/keda --namespace keda --version 2.14.0
kubectl apply -f prometheus/mysql-alerts.yaml -n monitoring
kubectl apply -f autoscaling/keda/biblio-api-so.yaml



# Pour tester
## Dans les environnements Linux, il est nécessaire d'installer les bibliothèques libmatthew afin de permettre la communication entre jocker et Docker sur les sockets unix locaux. Dans Ubuntu, il est nécessaire de :

sudo apt update
sudo apt install libunixsocket-java
cp /usr/lib/jni/libunix-java.so /usr/lib64/libmatthew-java/libunix-java.so

Instaler l'environement de python
sudo apt install python3-venv

# Maintenant, exécutez la commande suivante pour créer l’environnement virtuel :
python3 -m venv .venv

# Pour activer un environnement virtuel, entrez cette commande :
source .venv/bin/activate

# Si vous devez désactiver un environnement virtuel, exécutez simplement la commande suivante :
deactivate
rm -rf monenv

# installer les bibliotheques
apt-get update
pip install --upgrade pip

# installer les dependances à Python
pip install -r requirements.txt 

# donc pour chacun des projets
pip install -r biblio-app/requirements.txt 
pip install -r biblio-api/requirements.txt 