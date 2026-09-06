1.今日学习内容
mkdir -p ~/practice/day03 && cd ~/practice/day03	#创建day03文件

任务 1：vim 生存技能（40 分钟）
vim 只有三种模式，理解了这个就理解了一半：
普通模式（打开就是） --按 i/a/o--> 插入模式（能打字） --按 Esc--> 回普通模式
普通模式 --按 :--> 命令行模式（:wq 保存退出 / :q! 放弃退出）

vim practice.txt
按 i 进入插入模式，打 5 行字（比如 5 个设备名），按 Esc 回普通模式
dd 删除一行 → u 撤销回来（误删的后悔药）
光标移到第 2 行，yy 复制 → p 粘贴到下面，连按 3 次 p
/r1 回车搜索 → n 跳下一个匹配 → N 跳上一个
gg 回文件头，G 跳文件尾，x 删光标下的字符，o 在当前行下方开新行并进入插入模式
:set number 显示行号
:wq 保存退出
实战演练：用 vim 改一个真实配置——往 hosts 文件加一条记录并验证生效（改系统文件要 sudo）：
bash
sudo vim /etc/hosts
# 在文件末尾按 o，加一行：127.0.0.1   mytest.local
# :wq 保存
ping -c 2 mytest.local        # 能 ping 通 127.0.0.1，说明你的修改生效了
最强外挂：系统自带交互式教程 vimtutor，30 分钟通关，比任何文章都管用。今天时间够就跟一遍，不够就周末补：
bash
vimtutor        # 如果没有，先 sudo dnf install -y vim-enhanced

任务 2：find——按条件找文件（30 分钟）
bash
find /etc -name "*.conf"                    # 按文件名找（通配符要加引号）
find /etc -name "*.conf" -mtime -7          # 最近 7 天内改过的配置
find /var/log -type f -size +10M 2>/dev/null    # 大于 10M 的日志（2>/dev/null 把"权限不足"的报错丢掉）
find ~ -type d -name "practice"             # -type d 只找目录，-type f 只找文件
find /etc -name "ssh*"                      # 找 ssh 开头的（能找到 sshd_config）
-mtime 的含义记牢：-7 = 7 天以内，+7 = 7 天以前，7 = 恰好第 7 天。
网工场景迁移：设备上你翻 NMS 找"上周谁改过配置"；Linux 上一条 find /etc -name "*.conf" -mtime -7 就列出来了——以后查"配置被谁动了"全靠它。
任务 3：grep——在内容里捞针（30 分钟）
bash
grep -r "nameserver" /etc 2>/dev/null       # 递归找含 nameserver 的行（DNS 配置在哪几个文件里？）
grep -n "nameserver" /etc/resolv.conf       # -n 显示行号
sudo grep "Failed password" /var/log/secure # 捞登录失败记录（配合 Day 2 的 tail -f 理解）
sudo grep -c "Failed password" /var/log/secure   # -c 只数次数：被试了几次？
history | grep vim                          # 管道组合：找自己敲过的 vim 命令
常用选项一张表（贴进笔记）：
表格
选项	作用	类比
-r	递归搜目录	全网设备批量 display
-n	显示行号	日志定位到第几行
-i	忽略大小写	—
-v	反选（不含关键词的行）	exclude
-c	只统计次数	`	count`
grep 关键词 文件 ≈ 设备上的 display xxx | include 关键词，思维完全相通，只是 Linux 里能对任意文本用。

任务 4：笔记 + 打卡（15 分钟）
bash
cd ~/code/neteng-to-sre && vim notes/day03.md

2.验收
(1)vim 里误删了一段内容，按什么撤销？
答:使用U键撤销

(2)不看资料写出：找 /etc 下最近 7 天改过的 .conf 文件
答:find /etc -name "*.conf" -mtime -7

(3)/var/log/secure 里今天登录失败了多少次，一条命令数出来
答:sudo grep -c "Failed password" /var/log/secure     # 大写 F，和日志原文一致
# 或者加 -i 忽略大小写，更保险：
sudo grep -ci "failed password" /var/log/secure

sudo grep "$(date '+%b %e')" /var/log/secure | grep -c "Failed password"
# 先按当天日期（如 "Aug 30"）过滤出今天的日志，再数 Failed password
# Rocky 9 还可以用新一代日志工具：sudo journalctl -u sshd --since today | grep -ci "failed"

(4)vim 保存退出和放弃修改退出分别是什么？
答:保存退出是:wq，放弃修改是:q!

(5)hosts 文件加一条 127.0.0.1 test.local 后用什么命令验证生效？
答:ping -c 2 test.local
