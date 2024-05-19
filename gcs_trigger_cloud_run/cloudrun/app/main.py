import os
import logging
from typing import Dict

from fastapi import FastAPI
from google.cloud import storage

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

app = FastAPI()

def transfer_file(source_bucket_name, source_blob_name, destination_bucket_name):
    # GCS クライアントを初期化
    storage_client = storage.Client()

    # ソースバケットとブロブを取得
    source_bucket = storage_client.bucket(source_bucket_name)
    source_blob = source_bucket.blob(source_blob_name)

    # デスティネーションバケットを取得
    destination_bucket = storage_client.bucket(destination_bucket_name)
    destination_blob_name = source_blob_name

    # ファイルをコピー
    source_bucket.copy_blob(source_blob, destination_bucket, destination_blob_name)

    result = f"ファイル {source_blob_name} を {source_bucket_name} から {destination_bucket_name} に転送しました。"
    logger.info(result)
    return result

@app.post("/")
async def on_event(event:Dict):
    source_bucket = event.get("bucket")
    source_file = event.get("name")

    if os.getenv('DESTINATION_BUCKET_NAME'):
        destination_bucket = os.getenv('DESTINATION_BUCKET_NAME')
    else:
        error_no_bucket = "コピー先のバケット名がありません"
        logger.error(error_no_bucket)
        return error_no_bucket

    result = transfer_file(source_bucket, source_file, destination_bucket)
    return result
