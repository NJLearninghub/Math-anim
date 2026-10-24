"""Sarvam AI (Bulbul) text-to-speech service for manim-voiceover.

Set ``SARVAM_API_KEY`` in the environment (never commit it). Optional
overrides: ``SARVAM_MODEL``, ``SARVAM_SPEAKER``, ``SARVAM_LANGUAGE``,
``SARVAM_PACE``.

The API returns base64 WAV; it is re-encoded to MP3 because manim-voiceover
reads audio duration with ``mutagen.mp3.MP3``.
"""
import base64
import io
import os
import re
from pathlib import Path

import requests
from pydub import AudioSegment

from manim_voiceover.services.base import SpeechService

SARVAM_TTS_URL = "https://api.sarvam.ai/text-to-speech"
DEFAULT_MODEL = "bulbul:v3"
DEFAULT_SPEAKER = "shubh"
DEFAULT_LANGUAGE = "en-IN"
DEFAULT_PACE = 1.0
DEFAULT_SAMPLE_RATE = 24000
MAX_CHARS = 450  # per request; stays under the smallest per-model limit


def _split_text(text: str, limit: int = MAX_CHARS) -> list[str]:
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    chunks, current = [], ""
    for s in sentences:
        if current and len(current) + 1 + len(s) > limit:
            chunks.append(current)
            current = s
        else:
            current = f"{current} {s}".strip()
    if current:
        chunks.append(current)
    return chunks


class SarvamTTSService(SpeechService):
    """Human-like narration via Sarvam's Bulbul text-to-speech API."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        speaker: str | None = None,
        language: str | None = None,
        pace: float | None = None,
        sample_rate: int = DEFAULT_SAMPLE_RATE,
        timeout: float = 60.0,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.api_key = api_key or os.environ.get("SARVAM_API_KEY")
        if not self.api_key:
            raise RuntimeError(
                "SARVAM_API_KEY is not set. Export it (or add it as an "
                "environment secret) before rendering."
            )
        self.model = model or os.environ.get("SARVAM_MODEL", DEFAULT_MODEL)
        self.speaker = speaker or os.environ.get("SARVAM_SPEAKER", DEFAULT_SPEAKER)
        self.language = language or os.environ.get("SARVAM_LANGUAGE", DEFAULT_LANGUAGE)
        self.pace = float(pace if pace is not None else os.environ.get("SARVAM_PACE", DEFAULT_PACE))
        self.sample_rate = sample_rate
        self.timeout = timeout

    def _synthesize_chunk(self, text: str) -> AudioSegment:
        resp = requests.post(
            SARVAM_TTS_URL,
            headers={
                "api-subscription-key": self.api_key,
                "Content-Type": "application/json",
            },
            json={
                "text": text,
                "target_language_code": self.language,
                "speaker": self.speaker,
                "model": self.model,
                "pace": self.pace,
                "speech_sample_rate": self.sample_rate,
            },
            timeout=self.timeout,
        )
        if not resp.ok:
            raise RuntimeError(
                f"Sarvam TTS request failed ({resp.status_code}): {resp.text[:500]}"
            )
        audios = resp.json().get("audios") or []
        if not audios:
            raise RuntimeError(f"Sarvam TTS returned no audio: {resp.text[:500]}")
        return AudioSegment.from_file(io.BytesIO(base64.b64decode(audios[0])), format="wav")

    def generate_from_text(self, text: str, cache_dir=None, path=None, **kwargs) -> dict:
        cache_dir = Path(cache_dir if cache_dir is not None else self.cache_dir)

        input_data = {
            "input_text": text,
            "service": "sarvam",
            "model": self.model,
            "speaker": self.speaker,
            "language": self.language,
            "pace": self.pace,
            "sample_rate": self.sample_rate,
        }
        cached = self.get_cached_result(input_data, cache_dir)
        if cached is not None:
            return cached

        audio_path = path if path is not None else self.get_audio_basename(input_data) + ".mp3"

        audio = sum(
            (self._synthesize_chunk(c) for c in _split_text(text)),
            AudioSegment.empty(),
        )
        audio.export(str(cache_dir / audio_path), format="mp3")

        return {
            "input_text": text,
            "input_data": input_data,
            "original_audio": audio_path,
        }
