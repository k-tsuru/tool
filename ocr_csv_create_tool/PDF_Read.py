import os
import json
import re
from google.cloud import vision
from google.cloud import storage
from google.protobuf import json_format

# uriを記載
# OCR処理対象ファイル
gcs_source_uri = "【OCR処理対象先のgsutil URIを記載（gs://～）】"
# OCR処理後ファイル格納場所
gcs_destination_uri = "【OCR処理後の格納先のgsutil URIを記載（gs://～）】"

# バケット名を記載
bucket_name = "【対象のGCSのバケット名を記載】"

# 鍵ファイルを記載
# JSONの鍵ファイルは同じディレクトリに置くことを忘れずに！
credential_path = '【GCPサービスアカウント作成時に作成の鍵ファイル名を記載】'

# 鍵ファイルのパスを記載
os.environ['【鍵ファイルが格納されているファイルパスを記載】'] = credential_path

# VisionAIで指定のファイルをOCR処理
# 対象ファイルをPDFに指定
mime_type = 'application/pdf'
batch_size = 2
client = vision.ImageAnnotatorClient()

feature = vision.Feature(
    type_=vision.Feature.Type.DOCUMENT_TEXT_DETECTION)

# 対象のPDFファイルパスを設定
gcs_source = vision.GcsSource(uri=gcs_source_uri)

input_config = vision.InputConfig(
    gcs_source=gcs_source, mime_type=mime_type)

gcs_destination = vision.GcsDestination(uri=f"{gcs_destination_uri}/")
output_config = vision.OutputConfig(
    gcs_destination=gcs_destination, batch_size=batch_size)

async_request = vision.AsyncAnnotateFileRequest(
    features=[feature], input_config=input_config,
    output_config=output_config)

operation = client.async_batch_annotate_files(
    requests=[async_request])

print('Waiting for the operation to finish.')
operation.result(timeout=180)


storage_client = storage.Client()

match = re.match(r"gs://([^/]+)/(.+)", gcs_destination_uri)
bucket_name = match.group(1)
prefix = match.group(2)

bucket = storage_client.get_bucket(bucket_name)

# List objects with the given prefix, filtering out folders.
blob_list = [
    blob
    for blob in list(bucket.list_blobs(prefix=prefix))
    if not blob.name.endswith("/")
]
print("Output files:")
for blob in blob_list:
    print(blob.name)

output = blob_list[0]

# OCR処理後の判別した文字について画面に表示
json_string = output.download_as_bytes().decode("utf-8")
response = json.loads(json_string)

# The actual response for the first page of the input file.
first_page_response = response["responses"][0]
annotation = first_page_response["fullTextAnnotation"]

# Here we print the full text from the first page.
# The response contains more information:
# annotation/pages/blocks/paragraphs/words/symbols
# including confidence scores and bounding boxes
print("Full text:\n")
print(annotation["text"])
