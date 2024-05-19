<< COMMENTOUT
# 01_execute_deployment.shで実行しない場合はコメントアウト外して変数を設定してください。
REGION=asia-northeast1
PROJECT_ID=$(gcloud config get-value project)
SERVICE_ACCOUNT=gcs-trigger-cloud-run@${PROJECT_ID}.iam.gserviceaccount.com
SOURCE_BUCKET_NAME=source-gcs-trigger-cloud-run
DESTINATION_BUCKET_NAME=destination-gcs-trigger-cloud-run
COMMENTOUT

gsutil mb -p ${PROJECT_ID} -c standard -l asia-northeast1 gs://${SOURCE_BUCKET_NAME}
gsutil mb -p ${PROJECT_ID} -c standard -l asia-northeast1 gs://${DESTINATION_BUCKET_NAME}

#トリガー作成
gcloud eventarc triggers create ${SERVICE_NAME} \
    --destination-run-service=${SERVICE_NAME} \
    --destination-run-region=${REGION} \
    --location=${REGION} \
    --event-filters="type=google.cloud.storage.object.v1.finalized" \
    --event-filters="bucket=${SOURCE_BUCKET_NAME}" \
    --service-account=${SERVICE_ACCOUNT}

# トリガー確認
gcloud eventarc triggers list --location=${REGION}
