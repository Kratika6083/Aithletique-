# backend/voice/tts_engine.py
import asyncio
import edge_tts
import tempfile
import os
import subprocess
from pydub import AudioSegment
import platform

class VoiceCoach:
    def __init__(self):
        self.voice = "en-US-AriaNeural"

    def speak(self, text):
        try:
            asyncio.run(self._speak_blocking(text))
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self._speak_blocking(text))

    async def _speak_blocking(self, text):
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as mp3_fp:
                mp3_path = mp3_fp.name

            communicate = edge_tts.Communicate(text, self.voice)
            await communicate.save(mp3_path)

            wav_path = mp3_path.replace(".mp3", ".wav")
            sound = AudioSegment.from_mp3(mp3_path)
            sound.export(wav_path, format="wav")

            # Only for Windows (safe PowerShell playback)
            if platform.system() == "Windows":
                powershell_script = f"(New-Object Media.SoundPlayer '{wav_path}').PlaySync();"
                subprocess.run(["powershell", "-Command", powershell_script], check=True)

            os.remove(mp3_path)
            os.remove(wav_path)

        except Exception as e:
            print("[VoiceCoach ERROR]", e)
