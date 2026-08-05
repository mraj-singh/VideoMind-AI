from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import (
    RunnableLambda,
    RunnablePassthrough,
)
from langchain_chroma import Chroma

from core.vector_store import get_retriever
from core.llm import get_llm
from core.prompts import RAG_SYSTEM_PROMPT

import gc

from core.vector_store import load_vector_store


def format_docs(docs):
    """
    Format retrieved transcript chunks.
    """

    return "\n\n".join(
        f"[Chunk {doc.metadata.get('chunk_index', '?')}]\n"
        f"{doc.page_content}"
        for doc in docs
    )


def get_rag_prompt():
    """
    Return the RAG prompt template.
    """

    return ChatPromptTemplate.from_messages(
        [
            ("system", RAG_SYSTEM_PROMPT),
            ("human", "{question}"),
        ]
    )


def build_rag_chain(
    vector_store: Chroma,
):
    """
    Build a RAG chain from the vector store.
    """

    retriever = get_retriever(vector_store)

    rag_chain = (
        {
            "context": retriever
            | RunnableLambda(format_docs),
            "question": RunnablePassthrough(),
        }
        | get_rag_prompt()
        | get_llm()
        | StrOutputParser()
    )

    return rag_chain


def ask_question(
    cache_key: str,
    question: str,
) -> str:
    """
    Ask a question against a cached transcript.
    """

    print(f"\nQuestion: {question}")

    # Load vector DB
    vector_store = load_vector_store(
        cache_key
    )

    # Build temporary RAG chain
    rag_chain = build_rag_chain(
        vector_store
    )

    # Generate answer
    answer = rag_chain.invoke(question)

    print(f"Answer: {answer}")

    # Release resources
    del rag_chain
    del vector_store

    gc.collect()

    return answer