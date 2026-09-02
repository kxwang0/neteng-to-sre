#!/bin/bash
# 系统巡检脚本 v1：采集 CPU/内存/磁盘/端口，输出格式化报告

REPORT_DIR=~/reports
mkdir -p "$REPORT_DIR"                       # -p：存在不报错，没有则创建
REPORT="$REPORT_DIR/$(date +%F).txt"         # 按日期命名报告文件

{
  echo "========== 系统巡检报告 =========="
  echo "时间：$(date '+%F %T')"
  echo "主机：$(hostname)"
  echo
  echo "--- CPU 负载（1/5/15 分钟） ---"
  uptime | awk -F'average:' '{print $2}'
  echo
  echo "--- 内存 ---"
  free -h
  echo
  echo "--- 磁盘 ---"
  df -h
  echo
  echo "--- 监听端口 ---"
  ss -tlnp
  echo "=================================="
} > "$REPORT"                                # { } 命令组：整段输出统一重定向到文件

echo "报告已生成：$REPORT"
cat "$REPORT"
