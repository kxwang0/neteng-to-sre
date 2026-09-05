#!/bin/bash
#批量探测地址可达性
for ip in 223.5.5.5 114.114.114.114 192.168.30.1;do
	if ping -c 2 -W 1 "$ip" &> /dev/null; then
		echo "$ip  通"
	else
		echo "$ip  不通，需要排查！"
	fi
done
