# src/open_llm_vtuber/tts/voicevox_tts.py
import aiohttp, tempfile, uuid, os, asyncio
from loguru import logger
from .tts_interface import TTSInterface

class TTSEngine(TTSInterface):
    def __init__(self, host, speaker_id, speed_scale=1.0, pitch_scale=0.0, intonation_scale=1.0, volume_scale=1.0, pre_phoneme_length=0.1, post_phoneme_length=0.1):
        self.host = host
        self.speaker_id = speaker_id
        self.speed_scale = speed_scale
        self.pitch_scale = pitch_scale
        self.intonation_scale = intonation_scale
        self.volume_scale = volume_scale
        self.pre_phoneme_length = pre_phoneme_length
        self.post_phoneme_length = post_phoneme_length

    async def async_generate_audio(self, text: str, file_name_no_ext=None) -> str:
        async with aiohttp.ClientSession() as sess:
            # ① AudioQuery
            async with sess.post(
                f"{self.host}/audio_query",
                params={"text": text, "speaker": self.speaker_id},
                json={}
            ) as r:
                query = await r.json()
                # パラメータの適用
                query["speedScale"] = self.speed_scale
                query["pitchScale"] = self.pitch_scale
                query["intonationScale"] = self.intonation_scale
                query["volumeScale"] = self.volume_scale
                query["prePhonemeLength"] = self.pre_phoneme_length
                query["postPhonemeLength"] = self.post_phoneme_length

            # ② Synthesis (stream)
            async with sess.post(
                f"{self.host}/synthesis",
                params={"speaker": self.speaker_id},
                json=query
            ) as r:
                pcm = await r.read()

        # ③ ファイル保存
        name = file_name_no_ext or str(uuid.uuid4())
        out_path = os.path.join(tempfile.gettempdir(), f"{name}.wav")
        with open(out_path, "wb") as f:
            f.write(pcm)
        logger.debug(f"VOICEVOX audio saved -> {out_path}")
        return out_path

    # 同期メソッドは非同期版を再利用
    def generate_audio(self, text: str, file_name_no_ext=None) -> str:
        return asyncio.run(self.async_generate_audio(text, file_name_no_ext))
