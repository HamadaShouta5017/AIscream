# Django + Channels + Whisper で WebSocket が動作しなかった原因と対処法

---

## ❌ 原因：Djangoを `runserver` で起動していた

Django はデフォルトでは **WSGI**（HTTPのみ対応）モードで動作します。  
そのため、`python manage.py runserver` で起動すると **WebSocket は無効（404エラー）** になります。

---

## ✅ 状況の構成確認（設定自体は正しい）

- ✅ `consumers.py`：WebSocket 処理定義済み  
- ✅ `routing.py`：WebSocket用URL (`/ws/whisper/`) 設定済み  
- ✅ `asgi.py`：`ProtocolTypeRouter` で WebSocket を設定済み  
- ✅ `settings.py`：`ASGI_APPLICATION` に asgi.py を設定済み  

→ **起動方法のみ誤っていた**

---

## 🧨 ブラウザとサーバーのエラーログ

### ブラウザ側

WebSocket connection to 'ws://localhost:8000/ws/whisper/' failed:
Error during WebSocket handshake: Unexpected response code: 404


### サーバー側

"GET /ws/whisper/ HTTP/1.1" 404 2374



---

## ✅ 解決方法：ASGI 対応サーバーで起動する

### ① Daphne をインストール

```bash
pip install daphne

② サーバーを ASGI で起動
bash
コピーする
編集する
daphne whisper_project.asgi:application
③ 起動ログ例（成功）
nginx
コピーする
編集する
Starting server at tcp:port=8000:interface=127.0.0.1
📡 consumers.py の WebSocket 処理（音声受信）
python
コピーする
編集する
from channels.generic.websocket import AsyncWebsocketConsumer
import json

class WhisperConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        print("✅ WebSocket接続成功")

    async def receive(self, text_data=None, bytes_data=None):
        print("🟡 音声データ受信:", bytes_data)
        await self.send(text_data=json.dumps({"text": "テスト受信"}))
🎙️ index.html で音声を送信するコード（JavaScript）
html
コピーする
編集する
<script>
let socket = new WebSocket("ws://localhost:8000/ws/whisper/");
let audioChunks = [];

navigator.mediaDevices.getUserMedia({ audio: true }).then(stream => {
    const mediaRecorder = new MediaRecorder(stream);
    mediaRecorder.start();

    mediaRecorder.ondataavailable = e => {
        audioChunks.push(e.data);
    };

    setInterval(() => {
        if (audioChunks.length > 0) {
            const blob = new Blob(audioChunks, { type: "audio/wav" });
            audioChunks = [];

            blob.arrayBuffer().then(buffer => {
                socket.send(buffer);
            });
        }
    }, 3000);

    mediaRecorder.onstop = () => stream.getTracks().forEach(t => t.stop());
});

socket.onmessage = function(event) {
    const data = JSON.parse(event.data);
    document.getElementById("output").innerText += "\n" + data.text;
};
</script>
✅ 最終チェックリスト
項目	状況
WebSocket用の routing 設定	✅ routing.py に /ws/whisper/ がある
asgi.py 設定済み	✅ ProtocolTypeRouter で WebSocket 設定済み
settings.py に ASGI 設定	✅ ASGI_APPLICATION = 'whisper_project.asgi.application'
サーバー起動方法	❌ runserver → ✅ daphne whisper_project.asgi:application

🎉 まとめ
nginx
コピーする
編集する
python manage.py runserver → WebSocket 404（WSGIのため）
ASGI対応サーバー（例：Daphne）で起動 → WebSocket 正常動作
