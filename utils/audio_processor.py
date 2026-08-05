import os

import yt_dlp
from pydub import AudioSegment

from core.config import CHUNK_MINUTES
from core.cache import TEMP_DIR


def download_youtube_audio(
    url: str,
    output_path: str,
) -> str:
    """
    Download YouTube audio directly to the specified WAV path.
    """

    output_template = os.path.splitext(output_path)[0] + ".%(ext)s"

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_template,
        "restrictfilenames": True,
        "noplaylist": True,
        "quiet": False,
        "extractor_args": {
            "youtube": {
                "player_client": ["android"]
            }
        },
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "192",
            }
        ],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(
                url,
                download=True,
            )

        return output_path

    except Exception as e:
        raise RuntimeError(
            f"Failed to download YouTube audio:\n{e}"
        )


def convert_to_wav(
    input_path: str,
    output_path: str,
) -> str:
    """
    Convert any audio/video file to
    16kHz mono WAV.
    """

    if (
        input_path.lower().endswith(".wav")
        and os.path.abspath(input_path)
        == os.path.abspath(output_path)
    ):
        return output_path

    try:

        audio = AudioSegment.from_file(input_path)

        audio = (
            audio
            .set_channels(1)
            .set_frame_rate(16000)
        )

        audio.export(
            output_path,
            format="wav",
        )

        return output_path

    except Exception as e:
        raise RuntimeError(
            f"Failed to convert file to WAV:\n{e}"
        )


def prepare_audio(
    source: str,
    output_path: str,
) -> str:
    """
    Prepare a WAV file from either
    a YouTube URL or a local file.
    """

    if source.startswith(("http://", "https://")):

        print("Detected YouTube URL.")

        return download_youtube_audio(
            source,
            output_path,
        )

    print("Detected local file.")

    return convert_to_wav(
        source,
        output_path,
    )


def chunk_audio(
    wav_path: str,
    cache_key: str,
    chunk_minutes: int = CHUNK_MINUTES,
) -> list[str]:
    """
    Split a WAV file into fixed-size chunks.
    """

    print("Chunking audio...")

    TEMP_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    audio = AudioSegment.from_wav(wav_path)

    chunk_ms = chunk_minutes * 60 * 1000

    chunks = []

    for index, start in enumerate(
        range(0, len(audio), chunk_ms),
        start=1,
    ):

        chunk = audio[start:start + chunk_ms]

        chunk_path = (
            TEMP_DIR
            / f"{cache_key}_chunk_{index:03d}.wav"
        )

        chunk.export(
            str(chunk_path),
            format="wav",
        )

        chunks.append(
            str(chunk_path)
        )

    print(
        f"Audio ready — {len(chunks)} chunk(s)."
    )

    return chunks


def cleanup_chunks(
    chunks: list[str],
):
    """
    Delete temporary chunk files.
    """

    for chunk in chunks:

        try:

            if os.path.exists(chunk):
                os.remove(chunk)

        except Exception:
            pass