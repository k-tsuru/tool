import os
import json
import random
import random, string
import time
from urllib.request import urlopen
from bs4 import BeautifulSoup

print('===読込先の情報入力===')
dir_path = input('読込先のパスを入力してください。>>')
input_file_name = input('読込先のファイル名を入力してください。>>')

print('===出力先の情報入力===')
output_file_name = input('出力先のファイル名を入力してください。>>')

# 出力先の取得
output_file_path = os.path.join(dir_path, output_file_name)

# JSONファイルの取得
read_json_file = os.path.join(dir_path, input_file_name)

# JSONファイルの読み込み
json_open = open(read_json_file, 'r',encoding = 'utf-8')
json_load = json.load(json_open)

# スクレイピング開始URLの取得
start_url = json_load['Url']['startUrl']

# 検索キーワードの取得
json_load_keyword = json_load['element']
keyword = []

# 検索キーワードの格納
for keyword_value in json_load_keyword.values():
    keyword.append(keyword_value)

# スクレイピングスタートURL
html = urlopen(start_url)
data = html.read()
html = data.decode('utf-8')

# 一時ファイル作成先
default_file = 'tmp.txt'
tmp_file_path = os.path.join(dir_path, default_file)


# HTMLを解析
soup = BeautifulSoup(html, 'html.parser')

# 解析したHTMLから任意の部分のみを抽出（ここではtitleとbody）
title = soup.find("title")
body = soup.find("body")
href = soup.find("href")

# リンクスタート先の設定
link_start = ""
start_item = soup.find("link", rel="start")
link_start = start_item.get('href')
# 最後の"/"を削除
link_start = link_start[:-1]

# リンク先取得
html_link = []

for link_item in soup.find_all("a", class_="idens-morelink"):
    link = link_item.get('href')
    # リンク先格納
    html_link.append(link_start + link)

# カウント変数の宣言
no = 0

# CSVファイル作成
output_file = open(output_file_path, mode='w')

while no < len(html_link):
    html_text = ""
    keyword_text = ""
    html_text = urlopen(html_link[no])
    html_soup = BeautifulSoup(html_text,'html.parser')
    keyword_text = html_soup.get_text()
    keyword_text = keyword_text.encode('cp932', "ignore")
    f = open(tmp_file_path, mode='wb')
    f.truncate
    f.write(keyword_text)
    f.close
    str_row = ''
    with open(tmp_file_path, mode='r') as f:
        # html1行毎に確認
        for line in f:
            keyword_count = 0
            # JSONで指定したキーワード分確認
            while keyword_count < len(keyword):
                if keyword[keyword_count] in line:
                    str_row += line[:-1]
                    str_row += ","
                    str_row += html_link[no]
                    str_row += '\n'  
                keyword_count += 1
        # CSVファイルに書き込み
        output_file.write(str_row)  
    f.close   
    no += 1

    # サーバ負荷対策
    time.sleep(0.1)

output_file.close
