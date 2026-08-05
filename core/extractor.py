import os
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from core.llm import get_llm
from core.prompts import (
    ACTION_ITEMS_PROMPT,
    DECISIONS_PROMPT,
    QUESTIONS_PROMPT,
)

def wrap_text(text: str):
    return {"text": text}

def build_chain(system_prompt: str):
    """
    Build a reusable extraction chain.
    """
    llm = get_llm()

    return (
        RunnablePassthrough()
        | RunnableLambda(wrap_text)
        | ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                ("human", "{text}"),
            ]
        )
        | llm
        | StrOutputParser()
    )


def extract_action_items(transcript: str) -> str:
    """
    Extract explicit action items.
    """

    chain = build_chain(ACTION_ITEMS_PROMPT)
    
    return chain.invoke(transcript)


def extract_key_decisions(transcript: str) -> str:
    """
    Extract explicit decisions.
    """

    chain = build_chain(DECISIONS_PROMPT)
    return chain.invoke(transcript)


def extract_questions(transcript: str) -> str:
    """
    Extract open questions and follow-ups.
    """

    chain = build_chain(QUESTIONS_PROMPT)

    return chain.invoke(transcript)