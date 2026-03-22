from http.server import BaseHTTPRequestHandler
import json
import os
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)
        data = json.loads(body)

        task = data.get("task", "")
        feedback = data.get("feedback", "")

        prompt = f"""
あなたはADHD傾向のある中学生向けの生活支援コーチです。
以下のタスクを、動きやすい小さなステップに分解してください。

条件:
- 日本語
- 具体的
- 最初の一歩を小さく
- 最大5個
- 順番に並べる
- category と steps をJSONで返す

タスク: {task}
コメント: {feedback}

出力例:
{{
  "category": "勉強",
  "steps": ["机に座る", "問題集を開く", "1問だけやる"]
}}
"""

        try:
            response = client.responses.create(
                model="gpt-4.1-mini",
                input=prompt
            )

            text = response.output_text

            try:
                result = json.loads(text)
            except:
                result = {
                    "category": "その他",
                    "steps": ["やる場所に行く", task, "終わったらチェック"]
                }

            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(result, ensure_ascii=False).encode("utf-8"))

        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            error_result = {
                "error": str(e)
            }
            self.wfile.write(json.dumps(error_result, ensure_ascii=False).encode("utf-8"))
