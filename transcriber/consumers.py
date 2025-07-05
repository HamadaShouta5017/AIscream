from channels.generic.websocket import AsyncWebsocketConsumer
import json

class WhisperConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        print("✅ WebSocket接続成功")

    async def receive(self, text_data=None, bytes_data=None):
        print("🟡 音声データ受信:", bytes_data)
        # 仮で返信
        await self.send(text_data=json.dumps({"text": "テスト受信"}))
