#!/bin/bash
# 用法: ./top_failed_ips.sh [日志文件] [TOP个数]
# 功能: 统计登录失败IP的TOP N

LOG=${1:-/var/log/secure}	#第1个参数，没传就用默认值
TOPN=${2:-5}			#第2个参数，默认5

check_file() {			#函数:检查文件是否存在
	if [ ! -f "$LOG" ]; then
		echo “错误:日志文件 $LOG 不存在”
		exit 1		#非0退出码 = 告诉外界"我失败了"
	fi
}

report() {			#函数:核心统计
	echo "===== 登录失败 IP TOP $TOPN(来源: $LOG)====="
	sudo grep "Failed password" "$LOG" | awk '{print $(NF-3)}' | sort | uniq -c | sort -rn | head -"$TOPN"
}

check_file			#调用函数
report
