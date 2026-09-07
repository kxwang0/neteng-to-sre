import argparse

parser = argparse.ArgumentParser(description="网络设备批量采集工具")
parser.add_argument("-H", "--host", required=True, help="设备 IP")
parser.add_argument("-u", "--username", default="admin1", help="登录用户名")
parser.add_argument("-o", "--output", default="采集汇总.txt", help="输出文件名")
args = parser.parse_args()

print(args.host, args.username, args.output)
