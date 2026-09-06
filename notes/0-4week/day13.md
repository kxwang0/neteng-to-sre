Day 13 详细手册：性能观察与磁盘故障演练（约 2 小时）
今天学"系统体检"五件套，然后亲手制造一次故障再救回来——故障演练是最快的成长方式。

任务 0：GitHub 自测 + 热身（5 分钟）
bash
gtest
sudo dnf install -y epel-release          # htop 在 EPEL 仓库（社区额外软件包），先启用
sudo dnf install -y htop sysstat          # htop 更好用的 top；sysstat 提供 iostat

任务 1：五件套速览（35 分钟）
bash
top               # 交互：按 1 展开每核 CPU；按 M 按内存排序；按 P 按 CPU 排序；q 退出
htop              # 更直观，方向键操作，F10 退出
vmstat 1 5        # 每秒刷新共 5 次：r=运行队列 b=阻塞 si/so=交换
free -h           # 内存：看 available
df -h             # 磁盘：看 Use%
iostat -x 1 3     # 磁盘 IO：看 %util（接近 100% = 磁盘繁忙）
uptime            # load average：三个数 ÷ CPU 核数 ≈ 每核负载
关键判读：load average 要结合核数看——2 核机器 load 2.0 = 满载，4 核机器 load 2.0 = 半载。nproc 查看核数。

任务 2：制造高负载再观察（20 分钟）
bash
yes > /dev/null &        # 后台起一个吃 CPU 的死循环
top                      # 观察：yes 进程 CPU 近 100%，load 爬升
杀掉它的三种方式（重点掌握，生产上天天用）：
bash
# 方式 1：任务号（⚠️ 只在"起它的那个终端"里有效，换终端失效）
jobs                     # 先查真实编号：[1]+ 运行中  yes > /dev/null
kill %1                  # 用 jobs 显示的编号

# 方式 2：PID（最通用，任何终端都有效）
pgrep yes                # 查出 PID（或从 top 第一列抄）
kill <PID>

# 方式 3：按名字杀（不用查号）
pkill yes
任务号（%1）= 会话内的临时工牌，只对当前终端有效；PID = 全系统唯一的身份证号，排障时优先用 PID
kill %1 失效时的排查：jobs 查任务号，pgrep yes 或 ps aux | grep yes 查 PID
⚠️ 练 kill 只用自己起的 yes——top 里的 node 进程是 Cursor Remote-SSH 的服务端，杀了远程连接会断；systemd、sshd 同理不能碰
bash
uptime                   # 验证负载回落

任务 3：磁盘写满故障演练（45 分钟）——今天的高潮
第一幕：制造大文件
bash
dd if=/dev/zero of=~/bigfile bs=1M count=30000     # 造一个 30GB 文件
df -h /                                            # 看使用率明显上升
第二幕：扮演排查者——假设你现在不知道是谁占的，按标准流程找元凶：
bash
df -h                          # 第 1 步：哪个分区满了？→ /
sudo du -sh /* 2>/dev/null | sort -rh | head    # 第 2 步：哪个一级目录最大？
sudo du -sh /home/* 2>/dev/null | sort -rh | head   # 第 3 步：逐级往下钻
sudo find / -xdev -type f -size +1G 2>/dev/null     # 第 4 步：直接找超大文件
⚠️ 第 4 步的坑：-xdev = 不跨越文件系统边界。如果 df -h 显示 /home（或其他目录）是独立挂载的文件系统（如 LVM 的 rl-home 卷），从 / 起搜的 find 不会进入它——df 显示哪个挂载点满了，find 就以哪个挂载点为起点：sudo find /home -xdev -type f -size +1G。du 不受此限制（它逐目录统计会跨挂载点），所以 du 找到方向、find 精确打击，两个要配合用。
第三幕：处理与复盘
bash
rm ~/bigfile
df -h /                        # 确认回落
复盘三问写进笔记：定位顺序为什么是 df → du → find？生产环境日志撑爆磁盘能不能直接 rm（提示：被进程持有的日志文件 rm 后空间不释放，要 > 文件 清空或重启进程）？

任务 4：笔记 + 打卡（10 分钟）
notes/day13.md 要点：五件套各自看什么指标；load 与核数的关系；磁盘排查四步流程；被占用文件删除不释放空间的知识点。
bash
cd ~/code/neteng-to-sre
git add . && git commit -m "Day 13: 性能观察与磁盘故障演练"
gtest && git push

2.验收
(1)load average 三个数是什么？为什么要除以核数？
答:最近 1、5、15 分钟的平均负载（处于运行或等待状态的进程数）。要除以核数换算成"每核负载"才有意义：2 核机器 load 2.0 = 满载告急，4 核机器 load 2.0 = 只用了一半——不看核数无法判断高低

(2)内存压力看 free 输出的哪个字段？
答:available 列——它含可回收的缓存，才是真正能分配给新程序的内存

(3)磁盘满了，定位元凶的标准流程是什么？
答:df -h 定位满的分区 → du -sh /* | sort -rh | head 逐级下钻找大目录 → find / -xdev -type f -size +1G 直接找超大文件

(4)vmstat 输出里 r 列和 b 列分别代表什么？
答:r = 运行队列长度（等 CPU 的进程数，持续大于核数 = CPU 瓶颈）；b = 阻塞队列长度（等 IO 的进程数，持续不为 0 = IO 瓶颈）

(5)为什么被进程持有的日志文件 rm 掉空间不释放？正确处理是什么？
答:进程持有文件句柄时，rm 只删除目录项（文件名），数据块要等进程关闭句柄后才真正回收，所以空间不释放。正确处理：> 文件名 清空内容（空间立即释放，进程无感知），或重启持有该文件的进程


