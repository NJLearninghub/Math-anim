"""Offline text-to-speech service for manim-voiceover.

gTTS (Google) returns HTTP 403 from many cloud/datacenter IPs, so this
project uses pyttsx3 (espeak-ng backend) instead — fully offline, no API
key required.

manim-voiceover hard-codes ``mutagen.mp3.MP3`` to read audio duration, but
pyttsx3's espeak driver writes WAV data regardless of the requested file
extension. ``OfflineTTSService`` re-encodes that WAV to a real MP3 via
pydub/ffmpeg so duration lookups succeed.
"""
from pathlib import Path

import pyttsx3
from pydub import AudioSegment

from manim_voiceover.services.pyttsx3 import PyTTSX3Service

DEFAULT_VOICE = "gmw/en-us"   # espeak-ng: English (America)
DEFAULT_RATE = 165            # words per minute


class OfflineTTSService(PyTTSX3Service):
    """pyttsx3-based speech service that outputs valid MP3 files."""

    def __init__(self, voice: str = DEFAULT_VOICE, rate: int = DEFAULT_RATE, **kwargs):
        engine = pyttsx3.init()
        engine.setProperty("rate", rate)
        if voice is not None:
            engine.setProperty("voice", voice)
        super().__init__(engine=engine, **kwargs)

    def generate_from_text(self, text: str, cache_dir: str = None, path: str = None) -> dict:
        if cache_dir is None:
            cache_dir = self.cache_dir
        cache_dir = Path(cache_dir)

        input_data = {"input_text": text, "service": "offline_pyttsx3"}
        cached_result = self.get_cached_result(input_data, cache_dir)
        if cached_result is not None:
            return cached_result

        if path is None:
            audio_path = self.get_audio_basename(input_data) + ".mp3"
        else:
            audio_path = path

        mp3_path = Path(cache_dir) / audio_path
        wav_path = mp3_path.with_suffix(".wav")

        self.engine.save_to_file(text, str(wav_path))
        self.engine.runAndWait()
        self.engine.stop()

        AudioSegment.from_wav(str(wav_path)).export(str(mp3_path), format="mp3")
        wav_path.unlink()

        return {
            "input_text": text,
            "input_data": input_data,
            "original_audio": audio_path,
        }
