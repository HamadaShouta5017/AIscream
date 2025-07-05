from channels.generic.websocket import AsyncWebsocketConsumer
import whisper
import tempfile
import soundfile as sf
import json

model = whisper.load_model("base")  # small, mediumも可

class WhisperConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        print("WebSocket接続成功")

    async def receive(self, bytes_data=None):
        print("received!")
        # 音声バイナリを一時ファイルに書き込み
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as tmp_wav:
            await self.send(text_data=json.dumps({
                'text': result["text"]
            }))
            tmp_wav.write(bytes_data)
            tmp_wav.flush()
            result = model.transcribe(tmp_wav.name, language='ja')
            print("音声認識結果:", result["text"])
            await self.send(text_data=json.dumps({"text": result["text"]}))
