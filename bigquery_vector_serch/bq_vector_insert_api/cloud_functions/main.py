import os, time, json
import logging

# gen app
import asyncio
import asyncpg
import numpy as np
from flask import Flask, request, jsonify
from google.cloud import storage
from cloudevents.http import CloudEvent,from_http
import functions_framework
from langchain.document_loaders import PyPDFLoader
from langchain.embeddings import VertexAIEmbeddings
from langchain.llms import VertexAI
from langchain import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import AnalyzeDocumentChain
from langchain.chains.question_answering import load_qa_chain
from pgvector.asyncpg import register_vector

# logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)


# Gen App
def download_from_gcs(bucket_name:str, name:str, local_path:str):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(name)
    name = name.split("/")[-1]
    blob.download_to_filename(local_path)
    logger.info(f"File downloaded to {local_path}")

def bq_insert(page_num, page_metadata, description, filtered_data, embeddings_data, bucket_name:str, name:str):
    from google.cloud import bigquery
    # TODO(developer): Set table_id to the ID of table to append to.
    table_id = os.getenv('TABLE_ID')
    gcs_uri = f'gs://{bucket_name}/{name}'
    # Construct a BigQuery client object.
    client = bigquery.Client()
    rows_to_insert = [
        {"page_num":page_num,"page_metadata": json.dumps(page_metadata), "gcs_uri":gcs_uri, "description": description, "embeddings_data": embeddings_data, "filtered_data": filtered_data}        
    ]

    errors = client.insert_rows_json(table_id, rows_to_insert)  # Make an API request.
    if errors == []:
        logger.info("New rows have been added.")
    else:
        logger.error("Encountered errors while inserting rows: {}".format(errors))


def gen_summarize_pdf(bucket_name:str, name:str, local_path:str):
    # Generate summary of the pdf
    loader = PyPDFLoader(local_path)
    document = loader.load()

    llm = VertexAI(
        model_name="text-bison@001",
        max_output_tokens=256,
        temperature=0.1,
        top_p=0.8,
        top_k=40,
        verbose=True,
    )

    qa_chain = load_qa_chain(llm, chain_type="map_reduce")
    qa_document_chain = AnalyzeDocumentChain(combine_docs_chain=qa_chain)
    description = qa_document_chain.run(
    input_document=document[0].page_content[:5000],
    question="何についての文書ですか？日本語で2文にまとめて答えてください。")

    # Load pdf for generate embeddings
    text_splitter = RecursiveCharacterTextSplitter(
        separators=["\n", "。"],
        chunk_size=512,
        chunk_overlap=128,
        length_function=len,
    )
    pages = loader.load_and_split(text_splitter=text_splitter)

    # Create embeddings and inser data to BigQuery
    embeddings = VertexAIEmbeddings(model_name="textembedding-gecko-multilingual@latest")

    for page_num, page in enumerate(pages[:100]): # Limit the nubmer of pages to avoid timeout.
        embeddings_data = embeddings.embed_query(page.page_content)
        logger.info(embeddings_data)
        # Filtering data
        filtered_data = page.page_content.encode("utf-8").replace(b'\x00', b'').decode("utf-8")
        # await insert_doc(name, filtered_data, page.metadata, user_id, embeddings_data)
        logger.info("{}: processed chunk {} of {}".format(name, page_num, min([len(pages)-1, 99])))
        # bq insert
        bq_insert(page_num, page.metadata,  description, filtered_data , embeddings_data, bucket_name, name)
        time.sleep(0.5)

    return


# Triggered by a change in a storage bucket
@functions_framework.cloud_event
def bq_vector_insert_api(cloud_event: CloudEvent) -> tuple:
    logger.info(f"cloud_event.data: {cloud_event.data}")
    data = cloud_event.data

    event_id = cloud_event["id"]
    event_type = cloud_event["type"]
    bucket = data["bucket"]
    name = data["name"]
    metageneration = data["metageneration"]
    timeCreated = data["timeCreated"]
    updated = data["updated"]

    # Cloud Functions用のパス
    local_path = f"/tmp/{name.split('/')[-1]}"

    download_from_gcs(bucket, name, local_path)
    gen_summarize_pdf(bucket, name, local_path)

    return event_id, event_type, bucket, name, metageneration, timeCreated, updated
