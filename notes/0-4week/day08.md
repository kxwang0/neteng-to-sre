1.今日学习内容
Day 8 详细手册：Shell 脚本入门（约 2 小时）

第 1 周你敲的每条命令都是"一次性"的；今天开始把它们组装成可重复使用的脚本——自动化运维的最小单元。学完今天，Day 4 那条 TOP5 命令会变成带参数、会报错的真正工具。

任务 0：GitHub 自测 + 热身（5 分钟）
bash
gtest
mkdir -p ~/practice/day08 && cd ~/practice/day08

任务 1：第一个脚本（15 分钟）
bash
vim hello.sh
bash
#!/bin/bash
# 我的第一个脚本
echo "今天是 $(date '+%F %T')"
echo "主机名：$(hostname)"
bash
chmod +x hello.sh       # 加执行权限（Day 2 的知识用上了）
./hello.sh              # 运行方式 1：直接执行
bash hello.sh           # 运行方式 2：交给 bash 解释（不需要执行权限）
两个要点：
第一行 #!/bin/bash（shebang）告诉系统"用哪个解释器跑"，永远别省略
脚本写完必须 chmod +x 才能 ./ 执行，报 Permission denied 就想起 Day 2

任务 2：变量与三种引号（25 分钟）
bash
vim vars.sh
bash
#!/bin/bash
name="neteng"                      # ① 等号两边不能有空格！（新手第一坑）
today=$(date +%F)                  # ② $() 命令替换：把命令结果存进变量

echo "普通用法：$name"
echo "花括号用法：${name}_to_sre"   # ③ 和其他字符连写时必须加 {}
echo "单引号原样输出：'$name'"      # ④ 单引号里 $name 不展开
echo "双引号会展开：\"$name\""
echo "今天是：$today"
bash
chmod +x vars.sh && ./vars.sh
引号口诀：单引号是石头（里面什么都不解析），双引号是筛子（变量照常展开），$() 是管道口（把命令结果倒进来）。
实验：故意写 name = "neteng"（带空格）跑一次，看报什么错——踩过就记住了。

任务 3：判断与循环（40 分钟）——网工场景实战
先写"批量 ping 探测"脚本，这就是你以后自动化巡检的雏形：
bash
vim ping_check.sh
bash
#!/bin/bash
# 批量探测地址可达性
for ip in 223.5.5.5 114.114.114.114 192.168.100.254; do
  if ping -c 2 -W 1 "$ip" &> /dev/null; then
    echo "$ip  通"
  else
    echo "$ip  不通，需要排查！"
  fi
done
bash
chmod +x ping_check.sh && ./ping_check.sh
拆解知识点：
表格
语法	含义	备注
for ip in A B C; do ... done	循环，依次取值	网工批量操作的灵魂
if ...; then ... else ... fi	判断	注意结尾是倒写的 fi
ping -c 2 -W 1	发 2 个包、超时 1 秒	别让脚本卡在死地址上
&> /dev/null	把输出全部丢进黑洞	我们只关心成败，不看回显
if 命令	命令成功（退出码 0）走 then	Shell 判断的本质
数字比较写法（Day 9/10 巡检脚本要用）：[ $使用率 -gt 80 ]，记三个：-eq 等于、-gt 大于、-lt 小于。

任务 4：函数 + 改造 TOP5 脚本（30 分钟）——今天的毕业作品
把 Day 4 那条 TOP5 命令升级成带参数、会校验、可复用的脚本：
bash
vim top_failed_ips.sh
bash
#!/bin/bash
# 用法：./top_failed_ips.sh [日志文件] [TOP个数]
# 功能：统计登录失败 IP 的 TOP N

LOG=${1:-/var/log/secure}      # 第 1 个参数，没传就用默认值
TOPN=${2:-5}                   # 第 2 个参数，默认 5

check_file() {                 # 函数：检查文件是否存在
  if [ ! -f "$LOG" ]; then
    echo "错误：日志文件 $LOG 不存在"
    exit 1                     # 非 0 退出码 = 告诉外界"我失败了"
  fi
}

report() {                     # 函数：核心统计
  echo "===== 登录失败 IP TOP $TOPN（来源：$LOG）====="
  sudo grep "Failed password" "$LOG" | awk '{print $(NF-3)}' | sort | uniq -c | sort -rn | head -"$TOPN"
}

check_file                     # 调用函数
report
bash
chmod +x top_failed_ips.sh
./top_failed_ips.sh                        # 用默认值跑
./top_failed_ips.sh /var/log/secure 10     # 看 TOP 10
./top_failed_ips.sh /不存在的文件           # 看报错逻辑生效
$1、$2 是脚本收到的第 1、2 个参数；${1:-默认值} 的意思是"没传参数就用默认值"——这个写法以后天天见。

2.验收
(1)变量赋值 name = "test" 为什么报错？（空格问题）
答:Shell会把name当成命令、= 和 "test"当成参数来执行，报name:未找到命令。赋值语句等号两边不能有空格，有空格就不再是赋值语法了

(2)单引号和双引号包变量有什么区别？
答:单引号是"石头":里面的$name原样输出不展开，双引号是"筛子":$name 会被替换成变量的值

(3)for 循环和 if 判断的结尾分别是什么？（done 和 fi——倒过来写）
答:for循环以done结尾，if判断以fi结尾(if倒过来写)

(4)${1:-/var/log/secure} 这串符号是什么意思？
答:位置参数默认值写法:$1是脚本收到的第1给参数;${1:-/var/log/secure}表示"如果调用时没传第1给参数就使用默认值/var/log/secure"

(5)脚本里 exit 1 的作用？和正常退出有什么区别？
答:exit1以非0退出码终止脚本，告诉外界"我执行失败了"；正常结束(exit0或脚本自然跑完)表示成功。用echo$?可查看上一条命令的退出码--cron、其他脚本、未来的CI流水线都靠退出码判断成败



