1.今日学习内容
Day 9 详细手册：巡检脚本 v1（约 2 小时）
今天把前 8 天的零件组装成第一个真正有用的工具：系统巡检脚本。这是运维岗每天都在跑的东西。

任务 0：GitHub 自测 + 热身（5 分钟）
bash
gtest
mkdir -p ~/practice/day09 && cd ~/practice/day09

任务 1：采集命令单项突破（35 分钟）
先单独跑通每个采集命令，再考虑抠字段：
bash
uptime                              # CPU 负载（load average 三个数：1/5/15 分钟）
free -h                             # 内存（重点看 available 列，不是 free 列）
df -h                               # 磁盘使用率
ss -tlnp                            # 监听中的 TCP 端口及对应进程
top -bn1 | head -15                 # top 的"快照模式"，适合脚本采集
抠字段练习（Day 4 的功夫）：
bash
uptime | awk -F'average:' '{print $2}'                    # 只取负载三个数
free | awk '/Mem:/ {printf "内存使用率 %.1f%%\n", $3/$2*100}'
df -h / | awk 'NR==2 {print "根分区使用率 " $5}'           # NR==2 只取第 2 行

任务 2：组装 sys_check.sh v1（40 分钟）
bash
mkdir -p ~/code/neteng-to-sre/scripts
vim ~/code/neteng-to-sre/scripts/sys_check.sh
bash
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
bash
chmod +x ~/code/neteng-to-sre/scripts/sys_check.sh
~/code/neteng-to-sre/scripts/sys_check.sh

任务 3：体会重定向的两个细节（15 分钟）
bash
~/code/neteng-to-sre/scripts/sys_check.sh    # 再跑一次：同一天报告被覆盖（> 覆盖）
echo "追加一行" >> ~/reports/$(date +%F).txt  # >> 是追加
cat ~/reports/$(date +%F).txt                # 对比 > 和 >> 的差异

任务 4：笔记 + 打卡（10 分钟）
notes/day09.md 要点：抠字段三条命令各段含义；{ } > 文件 的作用；> vs >>；mkdir -p 为什么幂等。
bash
cd ~/code/neteng-to-sre
git add . && git commit -m "Day 9: 巡检脚本v1"
gtest && git push

2.验收
(1){ 多条命令 } > 文件 这个写法的作用？
答:{}是命令组:把花括号内所有命令的输出合并成一个整体，统一重定向到文件-->只写一次，不用每条命令各写一遍

(2)> 和 >> 的区别？巡检报告按日期命名时用哪个、为什么？
答:>覆盖写(原内容清空)、>>追加写。按日期命名的巡检日报用 >--同一天重跑要的是"最新一份完整报告"而不是拼接;运行日志采用 >>

(3)free -h 里评估内存压力应该看 free 列还是 available 列？为什么？
答:看available列:它包含可回收的缓存，是真正"还能分配给程序"的内存。free列只是"完全没被动过的"--Linux会把空闲内存拿去做缓存，free小不等于内存紧张

(4)ss -tlnp 四个选项各管什么？
答:t=TCP、|=监听中(listening)、n=数字显示(不解析服务名)、p=显示占用进程

(5)df -h / | awk 'NR==2 {print $5}' 里 NR==2 是什么意思？
答:NR是当前行号(Number of Record)，NR==2表示只处理第2行--第1行是df输出的表头，要跳过
