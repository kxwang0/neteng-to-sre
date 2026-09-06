# 闭卷练习用：不要看 backup.py，按注释把 # ??? 补全。
# 补完后：python3.12 空白骨架.py
# 卡超过 3 分钟就停，在下面「卡住的零件」里记一笔，再去翻对应那天的笔记。

import json
import os
import difflib
from datetime import date
from getpass import getpass
from netmiko import ConnectHandler

BACKUP_DIR = "backups"
DEVICES_FILE = "devices.json"


def load_devices(path):
    # 用 with open + json.load 读出设备清单
    # ???
    pass


def fetch_config(dev, password):
    # ConnectHandler 登录；send_command 抓配置；finally 里 disconnect
    # ???
    pass


def previous_lines(latest_path):
    # 没有 latest 返回 []；有就 splitlines()
    # ???
    pass


def save_backups(name, today, config):
    # 写 设备名_日期.txt 和 设备名_latest.txt
    # ???
    pass


def change_line_count(old_lines, new_text):
    # difflib.unified_diff + list + len
    # ???
    pass


def backup_one(dev, password, today):
    # 先读 latest，再采集，再 diff，最后落盘（顺序不能反）
    # ???
    pass


def main():
    # 建目录、取日期、getpass、for + try/except、最后打印 ok / failed
    # ???
    pass


if __name__ == "__main__":
    main()


# ----- 卡住的零件（练习后自己填，对照 Day 几）-----
# [ ] json.load
# [ ] ConnectHandler / send_command / disconnect
# [ ] with open 写文件
# [ ] os.path.exists + splitlines
# [ ] difflib.unified_diff
# [ ] try/except 单台失败不中断
# [ ] 先读 latest 再覆盖写（顺序）
