"""
Cache utilities for VideoMind AI.

This module stores and retrieves processed artifacts
such as transcripts, summaries and metadata.
"""
from urllib.parse import urlparse, parse_qs
import os
from pathlib import Path
import hashlib
import json
import shutil
from datetime import datetime
import gc
import time


# Directories

DATA_DIR = Path("data")

AUDIO_DIR = DATA_DIR / "audio"
TRANSCRIPT_DIR = DATA_DIR / "transcripts"
SUMMARY_DIR = DATA_DIR / "summaries"
VECTOR_DIR = DATA_DIR / "vectors"
REPORT_DIR = DATA_DIR / "reports"
TEMP_DIR = DATA_DIR / "temp"
HISTORY_FILE = DATA_DIR / "history.json"
CHAT_DIR = DATA_DIR / "chat"


for directory in [
    AUDIO_DIR,
    TRANSCRIPT_DIR,
    SUMMARY_DIR,
    VECTOR_DIR,
    REPORT_DIR,
    TEMP_DIR,
    CHAT_DIR,
]:
    directory.mkdir(parents=True, exist_ok=True)

# History File

if not HISTORY_FILE.exists():
    HISTORY_FILE.write_text(
        "[]",
        encoding="utf-8",
    )

# Helpers

def get_cache_key(source: str) -> str:
    """
    Generate a stable cache key.

    Priority:
    1. YouTube Video ID
    2. Local file hash
    """

    source = source.strip()

    if source.startswith(("http://", "https://")):

        parsed = urlparse(source)

        # youtube.com/watch?v=...
        if "youtube.com" in parsed.netloc:

            video_id = parse_qs(parsed.query).get("v")

            if video_id:
                return video_id[0]

        # youtu.be/VIDEO_ID
        elif "youtu.be" in parsed.netloc:

            return parsed.path.strip("/")

    # Local file
    absolute_path = os.path.abspath(source)

    return hashlib.md5(
        absolute_path.encode("utf-8")
    ).hexdigest()

# Transcript Cache

def transcript_exists(cache_key: str) -> bool:
    return (TRANSCRIPT_DIR / f"{cache_key}.txt").exists()


def save_transcript(
    cache_key: str,
    transcript: str,
):
    path = TRANSCRIPT_DIR / f"{cache_key}.txt"

    path.write_text(
        transcript,
        encoding="utf-8",
    )


def load_transcript(cache_key: str) -> str:
    path = TRANSCRIPT_DIR / f"{cache_key}.txt"

    return path.read_text(
        encoding="utf-8",
    )


# Summary Cache

def summary_exists(cache_key: str) -> bool:
    return (SUMMARY_DIR / f"{cache_key}.json").exists()


def save_summary(
    cache_key: str,
    result: dict,
):
    path = SUMMARY_DIR / f"{cache_key}.json"

    with open(
        path,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            result,
            f,
            indent=2,
            ensure_ascii=False,
        )


def load_summary(
    cache_key: str,
) -> dict:

    path = SUMMARY_DIR / f"{cache_key}.json"

    with open(
        path,
        encoding="utf-8",
    ) as f:

        return json.load(f)


# Vector Cache

def vector_exists(cache_key: str) -> bool:
    """
    Check whether a valid Chroma database exists.
    """

    vector_path = get_vector_path(cache_key)

    if not vector_path.exists():
        return False

    # Chroma always creates these files
    sqlite_file = vector_path / "chroma.sqlite3"

    return sqlite_file.exists()


def get_vector_path(cache_key: str) -> Path:
    return VECTOR_DIR / cache_key

# Audio Cache

def get_audio_path(cache_key: str) -> Path:
    """
    Return the cached WAV audio path.
    """
    return AUDIO_DIR / f"{cache_key}.wav"


def audio_exists(cache_key: str) -> bool:
    """
    Check whether cached audio exists.
    """
    return get_audio_path(cache_key).exists()

# History Cache

def load_history() -> list:
    """
    Load processed history.

    Returns an empty list if the history file
    does not exist, is empty, or is corrupted.
    """

    if not HISTORY_FILE.exists():
        return []

    try:

        with open(
            HISTORY_FILE,
            "r",
            encoding="utf-8",
        ) as f:

            content = f.read().strip()

            if not content:
                return []

            return json.loads(content)

    except (json.JSONDecodeError, OSError):

        return []


def save_history(history: list):
    """
    Save history safely.
    """

    with open(
        HISTORY_FILE,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            history,
            f,
            indent=2,
            ensure_ascii=False,
        )


def add_history_item(
    cache_key: str,
    title: str,
):
    """
    Add or update an analysis in history.

    Duplicate cache keys are removed first,
    then inserted at the top.
    """

    history = load_history()

    title = title.strip() if title else ""

    if not title:
        title = "Untitled Video"

    # Remove duplicate
    history = [
        item
        for item in history
        if item["cache_key"] != cache_key
    ]

    history.insert(
        0,
        {
            "cache_key": cache_key,
            "title": title,
            "processed_at": datetime.now().isoformat(
                timespec="seconds"
            ),
        },
    )

    # Keep latest 50 entries
    history = history[:50]

    save_history(history)


# Chat Cache

def get_chat_path(cache_key: str) -> Path:
    """
    Return chat history file path.
    """

    return CHAT_DIR / f"{cache_key}.json"


def chat_exists(cache_key: str) -> bool:
    """
    Check whether chat history exists.
    """

    return get_chat_path(cache_key).exists()


def save_chat(
    cache_key: str,
    messages: list,
):
    """
    Save complete chat history.
    """

    with open(
        get_chat_path(cache_key),
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            messages,
            f,
            indent=2,
            ensure_ascii=False,
        )


def load_chat(
    cache_key: str,
) -> list:
    """
    Load chat history.
    """

    path = get_chat_path(cache_key)

    if not path.exists():
        return []

    try:

        with open(
            path,
            "r",
            encoding="utf-8",
        ) as f:

            return json.load(f)

    except (
        json.JSONDecodeError,
        OSError,
    ):

        return []


def delete_chat(
    cache_key: str,
):
    """
    Delete saved chat history.
    """

    path = get_chat_path(cache_key)

    if path.exists():
        path.unlink()

def clear_all_cache():
    """
    Delete every cached analysis.
    """

    for directory in [
        AUDIO_DIR,
        TRANSCRIPT_DIR,
        SUMMARY_DIR,
        VECTOR_DIR,
    ]:

        shutil.rmtree(
            directory,
            ignore_errors=True,
        )

        directory.mkdir(
            parents=True,
            exist_ok=True,
        )

    save_history([])


def clear_all_cache():
    """
    Delete every cached artifact and recreate
    the cache directory structure.
    """

    gc.collect()

    directories = [
        AUDIO_DIR,
        TRANSCRIPT_DIR,
        SUMMARY_DIR,
        VECTOR_DIR,
        REPORT_DIR,
        TEMP_DIR,
        CHAT_DIR,
    ]

    # Delete directories

    for directory in directories:

        if directory.exists():

            for _ in range(3):

                try:

                    shutil.rmtree(
                        directory,
                        ignore_errors=False,
                    )

                    break

                except PermissionError:

                    gc.collect()

                    time.sleep(0.5)

    # Recreate directories

    for directory in directories:

        directory.mkdir(
            parents=True,
            exist_ok=True,
        )

    # Reset history

    HISTORY_FILE.write_text(
        "[]",
        encoding="utf-8",
    )