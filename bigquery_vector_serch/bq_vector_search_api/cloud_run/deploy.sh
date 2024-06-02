
PROJECT_ID=$(gcloud config get-value project)
REGION=asia-northeast1
SERVICE_NAME=bq-vector-search-api
REPOSITORY_NAME=bq-vector-search-api
SERVICE_ACCOUNT=bigquery-vector-search@${PROJECT_ID}.iam.gserviceaccount.com
DATASET=bigquery_vector_search
TABLE=pdf_embeddings

docker image build -t ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY_NAME}/${SERVICE_NAME}:latest .
gcloud builds submit --tag ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY_NAME}/${SERVICE_NAME}:latest

gcloud run deploy ${SERVICE_NAME} \
    --image ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY_NAME}/${SERVICE_NAME}:latest \
    --region ${REGION} \
    --service-account=${SERVICE_ACCOUNT} \
    --project=${PROJECT_ID} \
    --quiet \
    --set-env-vars PROJECT_ID=${PROJECT_ID},DATASET=${DATASET},TABLE=${TABLE}
