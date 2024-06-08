import os
from openai import OpenAI
import json
import base64

#端末に格納したAPI Keyの環境変数を設定
OpenAI.api_key = os.environ['OPENAI_API_KEY']

client = OpenAI()

# 一時的な読込措置（その１でOCR処理結果を格納したファイル）
path = 'D:\\work\\tool\\ocr_csv_create_tool\\text\\test_w.txt'

with open(path) as f:
    string = f.read()

# JSONファイル（試算表のスキーマ）を読み込む
path_json = 'D:\\work\\tool\\ocr_csv_create_tool\\json_config\\balancesheet_config.json'
with open(path_json, 'r', encoding='utf-8') as f:
    schema = json.load(f) 

# OCR処理したテキストファイルを指定したスキーマの形式にGPTで整理
response = client.chat.completions.create(
    model="gpt-4-turbo-preview",
    response_format={ "type": "json_object" },
    messages=[
      {"role": "system", "content": f"次の文字列から試算表の勘定科目毎の貸方残高・貸方合計・借方残高・借方合計を抜き出して、JSON形式で出力してください。JSONのスキーマは次の通りです：{schema}"},
      {"role": "user", "content": string}
    ]
  )

# GPTで整理した結果をJSONオブジェクトに変換
response_json = json.loads(response.choices[0].message.content)

# JSONオブジェクトを文字列に変換
json_str = json.dumps(response_json)

# 文字列をバイト列に変換してBase64エンコード
encoded_bytes = base64.b64encode(json_str.encode('utf-8'))

# エンコードされたバイト列を文字列に変換
encoded_str = encoded_bytes.decode('utf-8')

# エンコードされた文字列をデコードしてバイト列に戻す
decoded_bytes = base64.b64decode(encoded_str)

# バイト列を文字列にデコード
decoded_str = decoded_bytes.decode('utf-8')

print(str(decoded_bytes))

# 文字列をJSONオブジェクトに変換
decoded_data = json.loads(decoded_str)

# 一時的な記載（ファイル書き込み）
path_result = 'D:\\work\\tool\\ocr_csv_create_tool\\text\\test_result.json'

with open(path_result, 'w', encoding='utf-8') as f_json:
    json.dump(decoded_data, f_json)
