

# bq_vector_insert_api
pdfをエンべディングしてBigQueryに登録するAPI。
Cloud Functionsにデプロイ後
GCSのバケットにpdfファイルをアップロードすると起動します。


# bq_vector_serch_api
BigQueryのベクトル検索を利用してベクトル検索を行うAPI
Cloud Runにデプロイ後curlまたはFast APIのdocから文書検索を行います。


# Google Cloud サービスの準備
```
PROJECT_ID=$(gcloud config get-value project)
BUCKET_NAME=bigquery-vector-search
REGION=asia-northeast1
DATASET=bigquery_vector_search
TABLE=pdf_embeddings
REPOSITORY_NAME=bq-vector-search-api

#GCSバケット
gsutil mb -p ${PROJECT_ID} -c standard -l ${REGION} gs://${BUCKET_NAME}

#Artifact Registry
gcloud artifacts repositories create ${REPOSITORY_NAME} \
    --repository-format=docker \
    --location=${REGION} \
    --project=${PROJECT_ID}

#BigQuery データセット、テーブル
bq mk -d \
    --location=${REGION} \
    --project_id=${PROJECT_ID} \
    ${DATASET}

bq mk -t --schema schema.json ${DATASET}.${TABLE}
```

# サービスアカウント

```bash
PROJECT_ID=$(gcloud config get-value project)
SERVICE_ACCOUNT=bigquery-vector-search@${PROJECT_ID}.iam.gserviceaccount.com


while read role;do
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${SERVICE_ACCOUNT}" \
    --role=${role}
done << EOS
roles/aiplatform.user
roles/artifactregistry.serviceAgent
roles/bigquery.dataEditor
roles/bigquery.jobUser
roles/cloudfunctions.serviceAgent
roles/eventarc.eventReceiver
roles/eventarc.serviceAgent
roles/iam.serviceAccountTokenCreator
roles/pubsub.publisher
roles/run.serviceAgent
roles/run.developer
roles/run.invoker
roles/storage.objectViewer
EOS
```