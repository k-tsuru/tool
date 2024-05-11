import os
from google.cloud import storage

#クラウドストレージ（バケット）に接続
# 鍵ファイルを記載
credential_path = '【GCPサービスアカウント作成時に作成の鍵ファイル名を記載】'

# 鍵ファイルのパスを記載
os.environ['【鍵ファイルが格納されているファイルパスを記載】'] = credential_path

# バケット名を記載
bucket_name = "pdf_ocr_test_kyosuke_tsuru"

client = storage.Client()
bucket = client.get_bucket(bucket_name)

#ファイルをアップロード
input_dir_path = input('保存元のパスを入力してください。>>')
input_file_name = input('保存元のファイル名を入力してください。（PDF）>>')

read_pdf_file = os.path.join(input_dir_path, input_file_name)

blob = bucket.blob(input_file_name)
blob.upload_from_filename(filename=read_pdf_file)


