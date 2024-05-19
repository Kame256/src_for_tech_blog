
<< COMMENTOUT
# 01_execute_deployment.shで実行しない場合はコメントアウト外して変数を設定してください。
PROJECT_ID=$(gcloud config get-value project)
REGION=asia-northeast1
SERVICE_NAME=gcs-trigger-cloud-run
REPOSITORY_NAME=gcs-trigger-cloud-run
SERVICE_ACCOUNT=gcs-trigger-cloud-run@${PROJECT_ID}.iam.gserviceaccount.com
DESTINATION_BUCKET_NAME=destination-gcs-trigger-cloud-run
COMMENTOUT

gcloud artifacts repositories create ${REPOSITORY_NAME} \
    --repository-format=docker \
    --location=${REGION} \
    --project=${PROJECT_ID}

gcloud builds submit --tag ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY_NAME}/${SERVICE_NAME}:v1

gcloud run deploy ${SERVICE_NAME} \
    --image ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY_NAME}/${SERVICE_NAME}:v1 \
    --region ${REGION} \
    --service-account=${SERVICE_ACCOUNT} \
    --project=${PROJECT_ID} \
    --set-env-vars "DESTINATION_BUCKET_NAME=${DESTINATION_BUCKET_NAME}" \
    --quiet
