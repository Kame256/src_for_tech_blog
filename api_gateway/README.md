
# 概要
【Google Cloud】APIキー認証のAPI Gateway 作成方法


# Cloud Run デプロイ
・GAR:コンテナビルド
```

$ SERVICE_ACCOUNT="プロジェクトNo-compute@developer.gserviceaccount.com"
$ PROJECT_ID=$(gcloud config get-value project)

$ gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member="serviceAccount:${SERVICE_ACCOUNT}" \
  --role=""roles/storage.objectViewer""

$ gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member="serviceAccount:${SERVICE_ACCOUNT}" \
  --role="roles/cloudbuild.builds.builder"


$ gcloud run deploy for-api-gateway --region asia-northeast1 --source .

```

# API Gateway
```
# API作成
$ API_ID=for-api-gateway
$ PROJECT_ID=$(gcloud config get-value project)
$ gcloud api-gateway apis create $API_ID --project=${PROJECT_ID}


# APIコンフィグ作成
## api_definittion.yamlのaddressを修正
$ CONFIG_ID=for-api-gateway-config
$ API_DEFINITION=api_definittion.yaml

$ gcloud api-gateway api-configs create ${CONFIG_ID} \
  --api=${API_ID} --openapi-spec=${API_DEFINITION} \
  --project=${PROJECT_ID}


# API Gateway サービス有効化
$ gcloud services enable apigateway.googleapis.com
$ gcloud services enable servicemanagement.googleapis.com
$ gcloud services enable servicecontrol.googleapis.com

# ゲートウェイ作成
$ GATEWAY_ID=for-api-gateway
$ GCP_REGION=asia-northeast1

$ gcloud api-gateway gateways create ${GATEWAY_ID} \
  --api=${API_ID} --api-config=${CONFIG_ID} \
  --location=${GCP_REGION} --project=${PROJECT_ID}

# API Gateway有効化
$ gcloud api-gateway apis describe ${API_ID} # managedServiceを確認
$ MANAGED_SERVICE_NAME=#managedServiceの値

$ gcloud services enable ${MANAGED_SERVICE_NAME}
(API[詳細]のマネージド サービス)

# APIキー作成 
$ DISPLAY_NAME="For API Gateway"
$ gcloud beta services api-keys create --display-name=${DISPLAY_NAME} --project=${PROJECT_ID} #keyStringがapi key値
```
