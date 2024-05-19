
<< COMMENTOUT
# 01_execute_deployment.shで実行しない場合はコメントアウト外して変数を設定してください。
PROJECT_ID=$(gcloud config get-value project)
SERVICE_ACCOUNT_NAME=gcs-trigger-cloud-run
SERVICE_ACCOUNT=gcs-trigger-cloud-run@${PROJECT_ID}.iam.gserviceaccount.com
COMMENTOUT

# サービスアカウント作成
gcloud iam service-accounts create ${SERVICE_ACCOUNT_NAME} \
  --project=${PROJECT_ID} \
  --description="test gcs trigger for cloud run" \
  --display-name="${SERVICE_ACCOUNT_NAME}"

# サービスのAPI有効化
gcloud services enable artifactregistry.googleapis.com \
    cloudbuild.googleapis.com \
    eventarc.googleapis.com \
    run.googleapis.com \
    storage.googleapis.com \
    --project=${PROJECT_ID}

# IAMロールの付与
while read role ; do
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member=serviceAccount:${SERVICE_ACCOUNT} \
    --role=${role}
done < roles.txt

