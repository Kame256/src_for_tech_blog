import os
import logging
from typing import Dict
import json

# gen app
from fastapi import FastAPI
import numpy as np
from google.cloud import storage
from google.cloud import bigquery
from langchain.document_loaders import PyPDFLoader
from langchain.embeddings import VertexAIEmbeddings
from langchain.llms import VertexAI
from langchain import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import AnalyzeDocumentChain
from langchain.chains.question_answering import load_qa_chain
from pgvector.asyncpg import register_vector
from langchain.vectorstores.utils import DistanceStrategy
from langchain_community.vectorstores import BigQueryVectorSearch



# logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

# app
app = FastAPI()

async def search_doc_langchain(requests):
    embeddings = VertexAIEmbeddings(model_name="textembedding-gecko-multilingual@latest")
    embeddings_data = embeddings.embed_query(requests["question"])

    store = BigQueryVectorSearch(
        project_id=f"{requests['project']}",
        dataset_name=f"{requests['dataset']}",
        table_name=f"{requests['table']}",
        location="asia-northeast1",
        content_field = "filtered_data",
        metadata_field = "page_metadata",
        text_embedding_field = "embeddings_data",
        embedding=embeddings,
        distance_strategy=DistanceStrategy.EUCLIDEAN_DISTANCE,
    )
    docs = store.similarity_search_by_vector(embeddings_data, k=2)
    logger.info(f"docs : {docs}")
    context =  docs[0].page_content

    llm = VertexAI(
        model_name="text-bison@001",
        max_output_tokens=256,
        temperature=0.1,
        top_p=0.8,
        top_k=40,
        verbose=True,
    )

    template = """
    ###{context}###
    ###で囲まれたテキストから、"質問：{question}" に関連する情報を抽出してください。
    """

    prompt = PromptTemplate(
        input_variables=["context", "question"],
        template=template,
    )

    final_prompt = prompt.format(context=context, question=requests["question"])
    result = llm(final_prompt)

    return {
        "answer": result,
        "metadata": docs[0]
    }

async def search_doc_big_query(requests):

    # Crate embeddings
    embeddings = VertexAIEmbeddings(model_name="textembedding-gecko-multilingual@latest")
    embeddings_data = embeddings.embed_query(requests["question"])

    from . import vector_search_sql
    table_id = f"{requests['project']}.{requests['dataset']}.{requests['table']}"
    logger.info(f"table_id : {table_id}")
    query= vector_search_sql.create_vector_search_sql(table_id, str(embeddings_data))

    client = bigquery.Client()

    rows = list(client.query_and_wait(query))  # Make an API request.
    logger.info(f"rows : {rows}")
    context = rows[0]['filtered_data']

    llm = VertexAI(
        model_name="text-bison@001",
        max_output_tokens=256,
        temperature=0.1,
        top_p=0.8,
        top_k=40,
        verbose=True,
    )

    template = f"""
    ###{context}###
    ###で囲まれたテキストから、"質問：{requests["question"]}" に関連する情報を抽出してください。
    """

    prompt = PromptTemplate(
        input_variables=["context", "question"],
        template=template,
    )

    final_prompt = prompt.format(context=context, question=requests["question"])
    result = llm(final_prompt)

    return {
        "answer": result,
        "metadata": rows[0]
    }


@app.post("/search")
async def main(event:Dict):

    requests={"question": event["question"],"project":os.getenv("PROJECT_ID"),
              "dataset":os.getenv("DATASET"),"table":os.getenv("TABLE")}
    
    if None in requests.values():
        return {"error":"空のキーが存在します。"}

    logger.info(f"requests : {requests}")
    response = {}
    try:
        response["search_doc_big_query"] = await search_doc_big_query(requests)
        response["search_doc_langchain"] = await search_doc_langchain(requests)
    except Exception as e:
        logger.error(f"error : {e}")
        response["error"] = str(e)
    return response
