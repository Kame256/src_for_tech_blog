export PROJECT_ID=$(gcloud config get-value project)
export SERVICE_ACCOUNT_NAME=gcs-trigger-cloud-run
export SERVICE_ACCOUNT=gcs-trigger-cloud-run@${PROJECT_ID}.iam.gserviceaccount.com
export SERVICE_NAME=gcs-trigger-cloud-run
export REPOSITORY_NAME=gcs-trigger-cloud-run
export REGION=asia-northeast1
export SOURCE_BUCKET_NAME=source-gcs-trigger-cloud-run
export DESTINATION_BUCKET_NAME=destination-gcs-trigger-cloud-run

echo "sh create_service_account_enable_apis.sh"
sh create_service_account_enable_apis.sh || exit 1
cd cloudrun
echo "sh deploy.sh" || exit 1
sh deploy.sh
cd ..
echo "sh create_buckets_and_triggers.sh"
sh create_buckets_and_triggers.sh || exit 1
