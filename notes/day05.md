1.今日学习内容
Day 5 详细手册：systemd 服务管理 + cron 定时任务（约 2 小时）
今天两件事：让程序开机自动跑、崩溃自动拉起（systemd），以及让任务定时执行（cron）。这就是"自动化运维"的最小单元。

任务 0：GitHub 自测 + 热身（5 分钟）
bash
gtest
mkdir -p ~/practice/day05 && cd ~/practice/day05

任务 1：systemctl 玩转 sshd（30 分钟）
bash
systemctl status sshd          # 看状态：active (running)、enabled、PID、最近日志
systemctl is-active sshd       # 只问"活没活"
systemctl is-enabled sshd      # 只问"开机启不启"
sudo systemctl reload sshd     # 重载配置（不断连接，最安全）
sudo systemctl restart sshd    # 重启服务（已建立的 SSH 会话不会断，放心试）
systemctl list-units --type=service --state=running   # 系统里正在跑的所有服务
唯一禁令：远程连接时绝对不要 systemctl stop sshd——你会把自己关在门外（相当于在设备上把 VTY 全关了）。真关了就去 VMware 虚拟机窗口用控制台 systemctl start sshd 救回来。
四个动作的记忆法：start/stop 管"现在"，enable/disable 管"下次开机"，restart 管"现在重启"，reload 管"只重读配置"。改了配置用 reload，别动不动 restart——和设备上能热加载就不重启进程一个道理。

任务 2：手写一个 hello.service（40 分钟，今天的重头戏）
第 1 步：先写要被管理的脚本：
bash
sudo vim /usr/local/bin/hello.sh
内容：
bash
#!/bin/bash
while true; do
  echo "$(date '+%F %T') hello from systemd" >> /var/log/hello.log
  sleep 60
done
加执行权限：sudo chmod +x /usr/local/bin/hello.sh

第 2 步：写服务定义文件：
bash
sudo vim /etc/systemd/system/hello.service
内容（⚠️ unit 文件的注释必须单独成行，不能跟在配置后面，否则 # 后的内容会被当成配置值解析报错）：
ini
# [Unit] 段：这是什么、何时启动
[Unit]
Description=Hello systemd practice
After=network.target

# [Service] 段：跑什么、怎么守护
[Service]
Type=simple
ExecStart=/usr/local/bin/hello.sh
Restart=always

# [Install] 段：装到哪个启动级别
[Install]
WantedBy=multi-user.target

第 3 步：注册并启动：
bash
sudo systemctl daemon-reload            # 改了 unit 文件必做：让 systemd 重新读
sudo systemctl enable --now hello       # enable（开机自启）+ start（现在就跑）二合一
systemctl status hello                  # 看到 active (running) 即成功
tail -f /var/log/hello.log              # 等一分钟，看时间戳一条条冒出来

第 4 步：验证"故障自愈"（今天最有网工味的实验）：
bash
systemctl status hello | grep PID       # 记下当前 PID
sudo kill <PID>                         # 模拟进程崩溃，手动杀掉
sleep 3 && systemctl status hello       # 再看：被 Restart=always 拉起来了，PID 变了！
这就是 Linux 世界的"进程守护"，和你熟悉的设备 BFD/进程自动恢复一个思想——区别是这里一切都是你自己定义的。

第 5 步：验证开机自启：
bash
sudo reboot
# 重连后：
systemctl is-active hello               # active = 自启成功
tail -3 /var/log/hello.log              # 日志里有重启后的新时间戳
任务 3：cron 定时任务（25 分钟）
bash
crontab -e        # 进入编辑（默认用 vim，Day 3 的技能这里就用上了）
加一行（五个时间字段：分 时 日 月 周）：
plain
*/1 * * * * echo "$(date '+\%F \%T')" >> /home/kxwang/cron-test.log
cron 里的坑：% 在 crontab 里是特殊字符，必须写成 \% 转义，否则命令会被截断——这是新手 cron 不生效的第一大原因。
bash
crontab -l                  # 确认写进去了
sleep 70 && tail -3 ~/cron-test.log    # 等一分多钟，看到时间戳 = cron 生效
crontab -e                  # 练习完把这行删掉，别留垃圾任务
cron vs systemd 分工：跑"常驻服务"用 systemd（能守护、能看状态）；跑"到点执行一次"用 cron（备份、巡检、清理）。Day 10 的巡检脚本就会挂到 cron 上。

git add . && git commit -m "Day 5: systemd服务 + cron定时任务"

2.验收
(1)改完 sshd 配置文件后，用哪个命令让它生效最安全？
答:sudo systemctl reload sshd
reload 只让 sshd 重新读配置，不断任何现有连接，你当前的远程会话安然无恙。restart 也行（已建立的会话由子进程维持，不会断），但 reload 是"能热加载就不重启"的运维修养。改配置永远先试 reload，不行再 restart。

(2)unit 文件的三段 [Unit] [Service] [Install] 各管什么？
答:
表格
段	管什么	典型配置
[Unit]	这是什么、何时启动：描述、启动顺序依赖	Description=、After=network.target（等网络就绪再启动）
[Service]	跑什么、怎么守护：执行哪个程序、崩溃策略	ExecStart=、Type=、Restart=always
[Install]	装到哪一级：enable 时挂到哪个启动级别	WantedBy=multi-user.target（随正常系统启动）
一句话记法：Unit 管时机，Service 管运行，Install 管自启。

(3)进程被 kill 后自动拉起来，靠的是哪一行配置？
答:Restart=always，写在 [Service] 段。systemd 发现主进程退出就自动重新执行 ExecStart。其他常见值：no（不重启，默认）、on-failure（只在异常退出时重启）。

(4)新写了 .service 文件，直接 start 报找不到，大概率忘了什么命令？
答:sudo systemctl daemon-reload，systemd 会把 unit 文件缓存起来，新建或修改 unit 文件后必须让它重新加载一遍，否则它不知道新文件的存在。口诀：改了 unit 文件，先 daemon-reload。

(5)cron 行 */5 * * * * 是什么意思？里面的 % 为什么要转义？
答:五个字段依次是 分、时、日、月、星期。*/5 在"分"位上表示"每 5 分钟一次"（0、5、10、15…），其余位是 *（每位都匹配），整行含义：每 5 分钟执行一次
% 在 crontab 里是特殊字符，会被解析成换行，% 之后的内容被当成命令的标准输入——所以 date '+%F %T' 里的 % 必须写成 \%，否则命令到 % 就被截断了，任务自然不生效
