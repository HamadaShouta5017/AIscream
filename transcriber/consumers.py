import tempfile
import subprocess
import os
import whisper
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class WhisperConsumer(AsyncWebsocketConsumer):
    # クラス変数でモデルを1度だけ読み込む（負荷軽減）
    model = whisper.load_model("base")

    async def connect(self):
        await self.accept()
        print("🟢 WebSocket 接続確立")

    async def disconnect(self, close_code):
        print("🔴 WebSocket 切断:", close_code)

    async def receive(self, text_data=None, bytes_data=None):
        if bytes_data:
            print(f"🟢 バイナリ受信: {len(bytes_data)} bytes")

            # 一時ファイル作成（webm）
            with tempfile.NamedTemporaryFile(delete=False, suffix=".webm", mode="wb") as temp_input:
                temp_input.write(bytes_data)
                temp_input.flush()
                os.fsync(temp_input.fileno())  # OSのバッファも確実に書き出し
                input_path = temp_input.name

            # 一時ファイル作成（wav 出力先）
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_output:
                output_path = temp_output.name

            try:
                # ファイル存在確認ログ（デバッグ用）
                if not os.path.exists(input_path):
                    print(f"❗ 入力ファイルが存在しません: {input_path}")
                    await self.send(text_data=json.dumps({"error": "変換用ファイルが見つかりません"}))
                    return

                # ffmpegで変換
                result = subprocess.run([
                    "ffmpeg", "-y", "-i", input_path,
                    "-ar", "16000", "-ac", "1",
                    "-f", "wav", output_path
                ], capture_output=True, text=True)
                if result.returncode != 0:
                    print("❌ ffmpeg変換失敗:", result.stderr)
                    print("❌❌❌❌❌❌:")
                    await self.send(text_data=json.dumps({"error": "音声変換に失敗しました"}))
                    return

                print(f"✅ ffmpeg変換成功: {output_path}")

                # Whisperで文字起こし（クラス変数 model を使用）
                result = self.model.transcribe(output_path)

                print("📄 Whisper認識結果:", result["text"])
                await self.send(text_data=json.dumps({"text": result["text"]}))

            except Exception as e:
                print("❌ エラー:", str(e))
                await self.send(text_data=json.dumps({"error": "内部エラーが発生しました"}))

            finally:
                # 一時ファイルを削除
                for path in [input_path, output_path]:
                    try:
                        os.remove(path)
                    except Exception as cleanup_error:
                        print(f"⚠️ 一時ファイル削除失敗: {path} ({cleanup_error})")

        elif text_data:
            print("🟡 テキスト受信:", text_data)
            await self.send(text_data=json.dumps({"text": "テキストメッセージは未対応です"}))
