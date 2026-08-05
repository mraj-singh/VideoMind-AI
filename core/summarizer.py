from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_text_splitters import RecursiveCharacterTextSplitter
from core.llm import get_llm
from core.prompts import (
    MAP_SUMMARY_PROMPT,
    FINAL_SUMMARY_PROMPT,
    TITLE_PROMPT,
)
def split_transcript(transcript: str) -> list[str]:
    """
    Split long transcripts into manageable chunks
    for map-reduce summarization.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=3000,
        chunk_overlap=300,
    )

    return splitter.split_text(transcript)


def wrap_text(text: str):
    return {"text": text}


def summarize(transcript: str) -> str:
    """
    Generate a structured summary of a transcript using
    map-reduce summarization.
    """

    llm = get_llm()

    map_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", MAP_SUMMARY_PROMPT),
            ("human", "{text}"),
        ]
    )

    map_chain = map_prompt | llm | StrOutputParser()

    chunks = split_transcript(transcript)

    partial_summaries = [
        map_chain.invoke({"text": chunk})
        for chunk in chunks
    ]

    combined_summary = "\n\n".join(partial_summaries)

    combine_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", FINAL_SUMMARY_PROMPT),
            ("human", "{text}"),
        ]
    )
    combine_chain = (
        RunnablePassthrough()
        | RunnableLambda(wrap_text)
        | combine_prompt
        | llm
        | StrOutputParser()
    )

    return combine_chain.invoke(combined_summary)


def generate_title(transcript: str) -> str:
    """
    Generate a concise professional title.
    """

    llm = get_llm()

    title_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", TITLE_PROMPT),
            ("human", "{text}"),
        ]
    )

    title_chain = (
        RunnablePassthrough()
        | RunnableLambda(wrap_text)
        | title_prompt
        | llm
        | StrOutputParser()
    )

    return title_chain.invoke(transcript[:2000])
