PROJECT_ID=$(gcloud config get-value project)
BUCKET_NAME=bigquery-vector-search
REGION=asia-northeast1
SERVICE_ACCOUNT=bigquery-vector-search@${PROJECT_ID}.iam.gserviceaccount.com
DATASET=bigquery_vector_search
TABLE=pdf_embeddings


cat <<EOF > .env.yaml
TABLE_ID: ${PROJECT_ID}.${DATASET}.${TABLE}
EOF

# 第二代Cloud Functionsデプロイ
gcloud functions deploy bq_vector_insert_api \
--gen2 \
--memory=512MB \
--region=${REGION} \
--runtime=python311 \
--source=. \
--serve-all-traffic-latest-revision \
--trigger-event-filters="type=google.cloud.storage.object.v1.finalized" \
--trigger-event-filters="bucket=${BUCKET_NAME}" \
--service-account="${SERVICE_ACCOUNT}" \
--run-service-account="${SERVICE_ACCOUNT}" \
--trigger-service-account="${SERVICE_ACCOUNT}" \
--env-vars-file .env.yaml
