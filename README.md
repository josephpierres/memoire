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