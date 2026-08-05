import os

from faster_whisper import WhisperModel

from core.config import (
    WHISPER_MODEL,
    WHISPER_DEVICE,
    WHISPER_COMPUTE_TYPE,
)

_model = None


def load_model() -> WhisperModel:
    """
    Load the Faster-Whisper model once and reuse it.
    """

    global _model

    if _model is None:

        print(f"Loading Faster-Whisper model: {WHISPER_MODEL}")

        _model = WhisperModel(
            WHISPER_MODEL,
            device=WHISPER_DEVICE,
            compute_type=WHISPER_COMPUTE_TYPE,
            cpu_threads=os.cpu_count(),
        )

        print("Faster-Whisper model loaded.")

    return _model


def transcribe_chunk(chunk_path: str) -> str:
    """
    Transcribe a single audio chunk.
    """

    model = load_model()

    segments, info = model.transcribe(
        chunk_path,
        language="en",          # Skip language detection
        beam_size=1,            # Faster decoding
        vad_filter=True,
    )

    print(
        f"Detected Language: {info.language} "
        f"({info.language_probability:.2%})"
    )

    transcript = []

    for segment in segments:
        transcript.append(segment.text.strip())

    return " ".join(transcript).strip()


def transcribe_all(chunks: list[str]) -> str:
    """
    Transcribe all chunks and combine them into one transcript.
    """

    print("Using Faster-Whisper for transcription.")

    transcript = []

    total_chunks = len(chunks)

    for index, chunk in enumerate(chunks, start=1):

        print(
            f"Transcribing chunk {index}/{total_chunks}..."
        )

        transcript.append(
            transcribe_chunk(chunk)
        )

    print("Transcription complete.")

    return " ".join(transcript).strip()