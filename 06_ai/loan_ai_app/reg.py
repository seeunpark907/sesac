import os
import streamlit as st
from config import OPENAI_EMBEDDING_MODEL, PDF_PATH
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import AzureOpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from dotenv import load_dotenv

load_dotenv()

# 임베딩 객체 정의
@st.cache_resource
def get_embedding():
    return OpenAIEmbeddings(model=OPENAI_EMBEDDING_MODEL)

# vectorstore 생성/ 로드
@st.cache_resource
def get_vectorstore(
    persist_directory: str = "./jeonse_Chroma",
    collection_name: str = "jeonse_loan_products"
) -> Chroma:
    """
    Vectorstore가 존재하면 로드하고, 없으면 새로 생성합니다.
    """

    embedding = get_embedding()

    # 기존 vectorstore 로드 시도
    vectorstore_exists = (
        os.path.exists(persist_directory)
        and os.path.isdir(persist_directory)
    )

    if vectorstore_exists:
        
