"""
Central configuration for AI Video Assistant.
All project-wide constants should live here.
"""

import os

# LLM Configuration

LLM_PROVIDER = os.getenv(
    "LLM_PROVIDER",
    "groq",
)

GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.5-flash",
)

MISTRAL_MODEL = os.getenv(
    "MISTRAL_MODEL",
    "mistral-small-latest",
)

GROQ_MODEL = os.getenv(
    "GROQ_MODEL",
    "llama-3.3-70b-versatile",
)

TEMPERATURE = float(
    os.getenv("TEMPERATURE", "0.2")
)
# Whisper Configuration

WHISPER_MODEL = os.getenv(
    "WHISPER_MODEL",
    "small",
)

WHISPER_DEVICE = os.getenv(
    "WHISPER_DEVICE",
    "cpu",
)

WHISPER_COMPUTE_TYPE = os.getenv(
    "WHISPER_COMPUTE_TYPE",
    "int8",
)

# Embedding Configuration

EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "sentence-transformers/all-MiniLM-L6-v2",
)


# ChromaDB


CHROMA_DIR = "vector_db"
COLLECTION_NAME = "video_transcripts"


# Audio Processing


DOWNLOAD_DIR = "downloads"

CHUNK_MINUTES = 10


# Text Splitting


RAG_CHUNK_SIZE = 800
RAG_CHUNK_OVERLAP = 150

SUMMARY_CHUNK_SIZE = 3000
SUMMARY_CHUNK_OVERLAP = 300