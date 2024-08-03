API_GATEWAY_URL=
X_API_Key=
curl -X GET "${API_GATEWAY_URL}" \
     -H "Content-Type: application/json" \
     -H "X-API-Key: ${X_API_Key}"
