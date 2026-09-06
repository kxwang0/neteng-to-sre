1.今日学习
mkdir -p ~/practice/day04 && cd ~/practice/day04    #创建day04文件

任务 1：管道 | 的原理（25 分钟）
管道的含义一句话：前一个命令的输出，直接变成后一个命令的输入，屏幕上什么都不用经过你。
bash
ps aux | grep sshd          # 在所有进程里过滤出 sshd 相关
ps aux | grep sshd | grep -v grep   # 再去掉 grep 自己（grep -v 反选）
ls -l /etc | grep "\.conf"  # /etc 下的 conf 文件
history | tail -10          # 最近敲过的 10 条命令
cat /etc/passwd | wc -l     # 系统有多少个用户（行数=用户数）
体会一个细节：ps aux | grep sshd 的结果里总会混进一条 grep sshd 进程自己——所以老手写管道都会接 | grep -v grep，这是经验的味道。

任务 2：awk——按列抠数据（30 分钟）
awk 默认按空格/Tab 把每行切成列，$1 第 1 列、$2 第 2 列、$NF 最后一列：
bash
ps aux | awk '{print $1, $2, $11}'        # 只看 用户、PID、命令 三列
df -h | awk '{print $1, $5}'              # 只看 分区、使用率
awk -F: '{print $1, $7}' /etc/passwd      # -F: 改用冒号分列，看 用户名+登录Shell
ls -l | awk '{print $9, $5}'              # 文件名和大小
网工类比：awk 就是"从 display 输出里精确抠字段"——display interface brief 里你只想要接口名和状态两列时，干的就是这个事。
练习（自己写出来再看答案）：列出 /etc/passwd 里所有能用 bash 登录的用户名 → awk -F: '$7 ~ /bash/ {print $1}' /etc/passwd。

任务 3：sort + uniq 统计组合（25 分钟）
bash
awk -F: '{print $7}' /etc/passwd | sort                # 所有 Shell 排序
awk -F: '{print $7}' /etc/passwd | sort | uniq -c      # 每种 Shell 有多少人用
awk -F: '{print $7}' /etc/passwd | sort | uniq -c | sort -rn   # 按次数从多到少排
黄金组合记住它：sort | uniq -c | sort -rn | head = "统计 TOP N"。
三个细节：
uniq -c 前面必须先 sort（uniq 只合并相邻重复行）
sort -n 按数字排（不加 n，10 会排在 2 前面）；-r 倒序
head -5 截取前 5 行

任务 4：综合实战——统计登录失败 IP 的 TOP5（30 分钟）
今天的终极大考，把前面所有东西拼起来。先一步步拆开看，再组合：
bash
# 第 1 步：捞出失败日志
sudo grep "Failed password" /var/log/secure | head -5

# 第 2 步：观察格式，IP 在倒数第 4 列（... from IP port 端口 ssh2）
# 用 $(NF-3) 取倒数第 4 列——不管中间有没有 "invalid user" 都不会错位
sudo grep "Failed password" /var/log/secure | awk '{print $(NF-3)}' | head -5

# 第 3 步：套上黄金组合
sudo grep "Failed password" /var/log/secure | awk '{print $(NF-3)}' | sort | uniq -c | sort -rn | head -5
看懂了就把它存成一个可复用的命令（以后排查"谁在爆破服务器"直接用）：
bash
history | tail -1 >> ~/practice/day04/top5命令备份.txt
变体练习：统计失败登录的用户名 TOP5（提示：格式里有 "for root from" 和 "for invalid user admin from" 两种，试试 awk '{print $9}' 看会发生什么错位，体会为什么老司机爱用 $NF 系列）。

任务 5：笔记 + 打卡（15 分钟）
bash
cd ~/code/neteng-to-sre && vim notes/day04.md

2.验收
(1)ps aux | grep sshd 结果里为什么会混进一条 grep 自己？怎么去掉？
答:grep 运行时自己也是个进程，命令行里带着 "sshd" 字样，所以被 ps 抓到了。去掉的命令ps aux | grep sshd | grep -v grep

(2)不看资料写出"统计登录失败 IP TOP5"的完整命令
答:sudo grep "Failed password" /var/log/secure | awk '{print $(NF-3)}' | sort | uniq -c | sort -rn | head -5
#                              抠出 IP 之后：先排序 → 去重并计数 → 按次数倒序 → 取前 5

(3)uniq -c 前面为什么必须先 sort？
答:uniq只合并相邻重复行

(4)awk -F: 的 -F: 是什么意思？什么时候必须用它？
答:-F是改用冒号分列，当文件的分隔符不是空格/Tab 的时候。awk 默认只认空格和 Tab，/etc/passwd 这种用冒号分隔的文件，不加 -F: 的话 awk 会把整行当成一列，$1 取到的是整行内容。类似的还有逗号分隔的 CSV 文件（-F,）。

(5)sort -rn 的两个选项各管什么？少了 -n 会发生什么？
答:-r = reverse，倒序（结果从大到小），-n = numeric，按数字大小排序，少了 -n 不是"不排序"，而是按字符串字典序排，数字会排错——因为字符比较时 "1" < "2"，所以 10 会排在 2 前面。