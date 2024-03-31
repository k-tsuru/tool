import os
import json
import random
import random, string

print('===読込先の情報入力===')
input_dir_path = input('読込先のパスを入力してください。>>')
input_file_name = input('読込先のファイル名を入力してください。>>')

read_json_file = os.path.join(input_dir_path, input_file_name)

print('===出力先の情報入力===')
output_dir_path = input('保存先のパスを入力してください。>>')
output_file_name = input('保存するファイル名を入力してください。>>')
row_no = int(input('入力する行数を指定してください>>'))

new_file_path = os.path.join(output_dir_path, output_file_name)

# JSONファイルの読み込み
json_open = open(read_json_file, 'r')
json_load = json.load(json_open)

# ランダムで文字列入力
def randomname(n):
   return ''.join(random.choices(string.ascii_letters + string.digits, k=n))

# ランダムで数字入力
def randomvalue(start_no,end_no):
    random_value = random.randrange(start_no,end_no)
    return random_value

# CSVファイル作成行数の初期化
count = 0

# CSVファイル作成
f = open(new_file_path, mode='w')
while count < row_no:
    column_length = 0
    str_row = ''
    for json_value in json_load.values():
        if json_value['type'] == '1':
            str_row += randomname(json_value['element1'])
            str_row += ','
        elif json_value['type'] == '2':
            str_row += str(randomvalue(json_value['element1'],json_value['element2']))
            str_row += ','
    # 末尾1文字を削除
    f.write(str_row[:-1])
    f.write('\n')
    count += 1
f.close()
