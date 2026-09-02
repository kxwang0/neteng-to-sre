#!/bin/bash
# 系统巡检脚本 v1：采集 CPU/内存/磁盘/端口，输出格式化报告

REPORT_DIR=~/reports
mkdir -p "$REPORT_DIR"                       # -p：存在不报错，没有则创建
REPORT="$REPORT_DIR/$(date +%F).txt"         # 按日期命名报告文件

#日志函数，自动带时间戳
log() {
	echo "$(date '+%F %T') $1"
}

  log "========== 系统巡检报告 =========="
  log "时间：$(date '+%F %T')"
  log "主机：$(hostname)"
  log
  log "--- CPU 负载（1/5/15 分钟） ---"
  uptime | awk -F'average:' '{print $2}'
  log
  log "--- 内存 ---"
  free -h
  log
  log "--- 磁盘 ---"
  df -h
  log
  log "--- 监听端口 ---"
  ss -tlnp
  log "=================================="

#---磁盘告警---
usage=$(df / | awk 'NR==2 {print $5}' | tr -d '%')    # 抠出数字：去掉 % 号
if [ "$usage" -gt 80 ]; then
  log "【告警】根分区使用率 ${usage}%，超过阈值 80%！"
else
  log "【正常】根分区使用率 ${usage}%"
fi
 
 > "$REPORT"                                # { } 命令组：整段输出统一重定向到文件

log "报告已生成：$REPORT"
cat "$REPORT"
