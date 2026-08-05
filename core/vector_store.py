from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from core.config import (
    EMBEDDING_MODEL,
    COLLECTION_NAME,
    RAG_CHUNK_SIZE,
    RAG_CHUNK_OVERLAP,
)

from core.cache import get_vector_path


def get_embeddings() -> HuggingFaceEmbeddings:
    """
    Load the embedding model.
    """
    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )


def build_vector_store(
    transcript: str,
    cache_key: str,
) -> Chroma:
    """
    Build and persist a Chroma vector store.
    """

    print("Building Vector Store...")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=RAG_CHUNK_SIZE,
        chunk_overlap=RAG_CHUNK_OVERLAP,
        separators=[
            "\n\n",
            "\n",
            ". ",
            "? ",
            "! ",
            " ",
            "",
        ],
    )

    chunks = splitter.split_text(transcript)

    docs = [
        Document(
            page_content=chunk,
            metadata={
                "chunk_index": i,
                "source": "transcript",
            },
        )
        for i, chunk in enumerate(chunks)
    ]

    vector_store = Chroma.from_documents(
        documents=docs,
        embedding=get_embeddings(),
        collection_name=COLLECTION_NAME,
        persist_directory=str(get_vector_path(cache_key)),
    )

    return vector_store


def load_vector_store(cache_key: str) -> Chroma:
    """
    Load an existing Chroma vector store.
    """

    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=get_embeddings(),
        persist_directory=str(get_vector_path(cache_key)),
    )


def get_retriever(
    vector_store: Chroma,
    k: int = 5,
):
    """
    Create a retriever.
    """

    return vector_store.as_retriever(
        search_type="mmr",
        search_kwargs={
            "k": k,
        },
    )