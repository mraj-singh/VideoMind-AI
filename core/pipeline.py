"""
Pipeline orchestrator for VideoMind AI.

Coordinates the workflow:

Audio
    ↓
Transcription
    ↓
AI Analysis
    ↓
Vector Store
    ↓
RAG
"""

import time

from utils.audio_processor import (
    prepare_audio,
    chunk_audio,
    cleanup_chunks,
)

from core.transcriber import transcribe_all
from core.analysis import analyze_transcript

from core.vector_store import (
    build_vector_store,
    load_vector_store,
)

from core.cache import (
    get_cache_key,
    audio_exists,
    get_audio_path,
    transcript_exists,
    save_transcript,
    load_transcript,
    summary_exists,
    save_summary,
    load_summary,
    vector_exists,
    add_history_item,
    load_chat,
)


def execute_step(step_name: str, func, *args, **kwargs):
    """
    Execute a pipeline step with
    consistent logging and timing.
    """

    print(f"\n▶ {step_name}")

    start = time.perf_counter()

    try:

        result = func(*args, **kwargs)

        elapsed = time.perf_counter() - start

        print(f"✅ {step_name} completed in {elapsed:.2f}s")

        return result

    except Exception as e:

        raise RuntimeError(
            f"{step_name} failed.\nReason: {e}"
        ) from e

def print_performance_report(
    timings: dict,
):
    """
    Print pipeline performance summary.
    """

    print("\n" + "=" * 50)
    print("⚡ Performance Report")
    print("=" * 50)

    for stage, seconds in timings.items():

        if isinstance(seconds, bool):
            continue

        print(
            f"{stage:<22}"
            f"{seconds:>8.2f} sec"
        )

    print("=" * 50)

def run_pipeline(source: str,progress=None,) -> dict:
    """
    Execute the complete VideoMind AI pipeline.
    """

    print("\n🚀 Starting VideoMind AI\n")

    pipeline_start = time.perf_counter()

    timings = {}

    cache_key = get_cache_key(source)

    audio_path = str(
        get_audio_path(cache_key)
    )

    # Step 1 : Prepare Audio

    stage_start = time.perf_counter()

    if audio_exists(cache_key):

        print("✅ Using cached audio.")

    else:

        execute_step(
            "Preparing Audio",
            prepare_audio,
            source,
            audio_path,
        )

    timings["Audio Preparation"] = (
        time.perf_counter() - stage_start
    )
    if progress:
        progress.update(
            10,
            "Preparing audio..."
        )

    # Step 2 : Chunk Audio

    stage_start = time.perf_counter()

    chunks = execute_step(
        "Chunking Audio",
        chunk_audio,
        audio_path,
        cache_key,
    )

    timings["Chunking"] = (
        time.perf_counter() - stage_start
    )
    if progress:
        progress.update(
            25,
            "Chunking audio..."
        )

    # Step 3 : Transcript

    stage_start = time.perf_counter()

    if transcript_exists(cache_key):

        print("✅ Using cached transcript.")

        transcript = load_transcript(
            cache_key
        )

        cleanup_chunks(chunks)

    else:

        transcript = execute_step(
            "Transcribing Audio",
            transcribe_all,
            chunks,
        )

        cleanup_chunks(chunks)

        save_transcript(
            cache_key,
            transcript,
        )

    timings["Transcription"] = (
        time.perf_counter() - stage_start
    )

    print(
        f"\nTranscript Preview:\n"
        f"{transcript[:300]}...\n"
    )

    if progress:
        progress.update(
            45,
            "Transcribing..."
        )

    # Step 4 : AI Analysis

    stage_start = time.perf_counter()

    if summary_exists(cache_key):

        print("✅ Using cached AI Report.")

        cached = load_summary(
            cache_key
        )

        title = cached["title"]
        summary = cached["summary"]

    else:

        analysis = execute_step(
            "AI Analysis",
            analyze_transcript,
            transcript,
        )

        title = analysis["title"]
        summary = analysis["summary"]

        save_summary(
            cache_key,
            {
                "title": title,
                "summary": summary,
            },
        )

    timings["AI Analysis"] = (
        time.perf_counter() - stage_start
    )

    if progress:
        progress.update(
            70,
            "Generating AI report..."
        )
    # Step 5 : Vector Store

    stage_start = time.perf_counter()

    if vector_exists(cache_key):

        print(
            "✅ Using cached vector database."
        )

        vector_store = execute_step(
            "Loading Vector Store",
            load_vector_store,
            cache_key,
        )

    else:

        vector_store = execute_step(
            "Building Vector Store",
            build_vector_store,
            transcript,
            cache_key,
        )

    timings["Vector Store"] = (
        time.perf_counter() - stage_start
    )
    if progress:
        progress.update(
            90,
            "Building knowledge base..."
        )

    # Step 6 : Build RAG

    stage_start = time.perf_counter()

    if progress:
        progress.complete()
    # History

    add_history_item(
        cache_key=cache_key,
        title=title,
    )

    timings["Total"] = (
        time.perf_counter()
        - pipeline_start
    )

    print_performance_report(
            timings
    )

    print("\n✅ VideoMind AI Ready!\n")

    return {
        "cache_key": cache_key,
        "title": title,
        "transcript": transcript,
        "summary": summary,
        "messages": [],
        "timings": timings,
    }

def load_cached_pipeline(cache_key: str) -> dict:
    """
    Load a previously processed analysis from cache.
    """

    if not transcript_exists(cache_key):
        raise FileNotFoundError(
            "Transcript cache not found."
        )

    if not summary_exists(cache_key):
        raise FileNotFoundError(
            "Summary cache not found."
        )

    transcript = load_transcript(
        cache_key
    )

    summary_data = load_summary(
        cache_key
    )

    if not vector_exists(cache_key):
        raise FileNotFoundError(
            "Vector store cache not found."
        )

    vector_store = execute_step(
        "Loading Vector Store",
        load_vector_store,
        cache_key,
    )

    messages = load_chat(cache_key)

    return {
        "cache_key": cache_key,
        "title": summary_data["title"],
        "transcript": transcript,
        "summary": summary_data["summary"],
        "messages": messages,
        "timings": {
            "Loaded From Cache": True,
        },
    }