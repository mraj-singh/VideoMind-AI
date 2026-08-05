import os

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_mistralai import ChatMistralAI
from langchain_groq import ChatGroq

from core.config import (
    LLM_PROVIDER,
    GEMINI_MODEL,
    MISTRAL_MODEL,
    GROQ_MODEL,
    TEMPERATURE,
)


def get_llm():
    """
    Return the configured LLM provider.
    """

    provider = LLM_PROVIDER.strip().lower()

    
    # Google Gemini
    

    if provider == "gemini":

        api_key = os.getenv("GOOGLE_API_KEY")

        if not api_key:
            raise ValueError(
                "GOOGLE_API_KEY not found in environment."
            )

        print("Provider :", provider)
        print("Model    :", GEMINI_MODEL)

        return ChatGoogleGenerativeAI(
            model=GEMINI_MODEL,
            google_api_key=api_key,
            temperature=TEMPERATURE,
        )

    
    # Mistral
    
    if provider == "mistral":

        api_key = os.getenv("MISTRAL_API_KEY")

        if not api_key:
            raise ValueError(
                "MISTRAL_API_KEY not found in environment."
            )

        print("Provider :", provider)
        print("Model    :", MISTRAL_MODEL)

        return ChatMistralAI(
            model=MISTRAL_MODEL,
            mistral_api_key=api_key,
            temperature=TEMPERATURE,
        )

    
    # Groq
    

    if provider == "groq":

        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError(
                "GROQ_API_KEY not found in environment."
            )

        print("Provider :", provider)
        print("Model    :", GROQ_MODEL)

        return ChatGroq(
            model=GROQ_MODEL,
            api_key=api_key,
            temperature=TEMPERATURE,
        )

    raise ValueError(
        f"Unsupported LLM provider: {LLM_PROVIDER}"
    )