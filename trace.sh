curl --request GET \
  --url http://localhost:8000/getAllBooks \
  --header 'traceparent: 00-df853039b602c93e641526aaa7d67b8c-339f2b7a83c7d606-01'
curl --request GET \
  --url http://localhost:8082/getAllBooks \
  --header 'traceparent: 00-df853039b602c93e641526aaa7d67b8c-339f2b7a83c7d606-01'
