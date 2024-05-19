## 概要
Eventarc を使用して Cloud Storage トリガーによる Cloud Run の設定を行います。

## 機能
対象の GCS バケットにファイルがアップロードされると、指定された別のバケットへファイルを自動的にコピーします。

・サービスの処理
```
1. 対象のGCSバケットにファイルがアップロードされると Cloud Run のサービスが起動します。
2. アップロードされたバケット名とファイル名を取得します。
3. アップロードされたファイルを別のバケットにコピーします。
```

## 作成手順
・作成手順
```md:作成手順
1. サービスアカウントの作成およびAPIの有効化
2. Cloud Runサービスのデプロイ
3. バケットおよび Eventarc の設定
```

`sh 01_run_all_deployment.sh` を実行してサービスをデプロイします。ファイル内の環境変数は適宜修正してください。

バケットにファイルをアップロードすると、設定が正しく動作しているかテストできます。
```bash:test
echo "hello" > test.txt
gsutil cp test.txt gs://${SOURCE_BUCKET_NAME}
gsutil ls gs://${DESTINATION_BUCKET_NAME}
gcloud logging read "resource.labels.service_name=$SERVICE_NAME AND textPayload:test.txt" --format=json

```

使用後は以下のコマンドでサービスを削除できます。変数は適宜修正してください。
```sh:clean up
gcloud artifacts repositories delete ${REPOSITORY_NAME} \
    --location=${REGION}

gcloud run services delete ${SERVICE_NAME} \
    --region ${REGION}

gcloud eventarc triggers delete ${SERVICE_NAME} \
    --location=${REGION}

# バケット名は手動で編集してください
# "gcloud storage rm --recursive gs://" でGCS内の全てのバケット・オブジェクトが削除されます。
gcloud storage rm --recursive gs://SOURCE_BUCKET_NAME
gcloud storage rm --recursive gs://DESTINATION_BUCKET_NAME
```