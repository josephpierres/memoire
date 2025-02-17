kubectl delete -f autoscaling/jolie/adaptation-service.yaml
docker build -t adaptation-service autoscaling/jolie/
docker image tag adaptation-service  pjoseph5011/adaptation-service
docker push pjoseph5011/adaptation-service
kubectl apply -f autoscaling/jolie/adaptation-service.yaml
kubectl get pods -n monitoring