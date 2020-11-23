# パスワードの初期データを生成する。
#
# 初期データ生成
#   python tools/pw.py generate

import sys
import random
import datetime

JST = datetime.timezone(datetime.timedelta(hours=+9))

def generate(write=False):
    start_time_list = []
    # 11/22 9:00 から 10 分おきに、18:00 まで
    start_time_list.extend(datetime.datetime(2020, 11, 22, h, m, 0, tzinfo=JST) for h in range(9, 18) for m in range(0, 60, 10))
    # 11/23 9:00 から 10 分おきに、18:00 まで
    start_time_list.extend(datetime.datetime(2020, 11, 23, h, m, 0, tzinfo=JST) for h in range(9, 18) for m in range(0, 60, 10))
    items = []
    alphabet = list(set(range(ord('A'), ord('Z') + 1)) - set([ord('I'), ord('O')]))
    for start_time in start_time_list:
        # 数字4桁 + 英大文字1文字 (I, O を除く)
        password = '%04d%c' % (random.randint(0000, 9999), random.choice(alphabet))
        end_time = start_time + datetime.timedelta(minutes=5)
        print('\t'.join([password, start_time.isoformat(), end_time.isoformat()]))

def main(cmd):
    if cmd == 'generate':
        generate()

if __name__ == '__main__':
    main(*sys.argv[1:])
