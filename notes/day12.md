1.今日学习内容
Day 12 详细手册：Linux 网络排障工具箱（约 2 小时）
今天是你的"主场升级"：把设备上的排障套路平移到 Linux。学完这天，K8s 时代最值钱的"Service 不通怎么查"你已经有了地基。

任务 0：GitHub 自测 + 热身（5 分钟）
bash
gtest
mkdir -p ~/practice/day12 && cd ~/practice/day12

任务 1：ip 三件套（25 分钟）
bash
ip addr                    # ≈ display ip interface brief
ip route                   # ≈ display ip routing-table
ip -s link                 # ≈ display interface（带收发计数/错包统计）
ip route get 223.5.5.5     # 查"去这个地址走哪条路由、从哪个口出"——排障神器
对比练习：把每条命令的输出和你在设备上对应的 display 输出对照，写在笔记里。

任务 2：ss——端口与连接（20 分钟）
bash
ss -tlnp                   # 监听中的 TCP 端口（Day 9 巡检脚本用过）
ss -tnp state established  # 当前已建立的连接
ss -tlnp | grep :22        # 确认 sshd 在监听 22
ss -s                      # 连接统计总览
选项记法：t=TCP、l=监听中、n=不解析（数字显示）、p=显示进程。以后排查"服务起来了但连不上"，第一步就是 ss -tlnp | grep 端口 看它到底在没在监听、监听在哪个地址（127.0.0.1 和 0.0.0.0 的区别，你懂的）。

任务 3：tcpdump 抓包（45 分钟）——今天的重头戏
实验一：抓 ICMP
bash
# 终端 A
sudo tcpdump -i any icmp -nn
# 终端 B
ping -c 3 127.0.0.1
# A 里看 echo request / reply 成对出现
实验二：抓 TCP 三次握手 + 四次挥手（对着理论看自己抓的包）
bash
# 终端 A
sudo tcpdump -i lo tcp port 22 -nn
# 终端 B：发起一次 SSH 连接再退出
ssh kxwang@127.0.0.1 exit
在 A 里按时间顺序找到标志位序列：[S] → [S.] → [.]（三次握手 SYN、SYN-ACK、ACK），连接结束时找 [F.] 开头的四次挥手序列。
常用选项：-nn 不解析域名和端口名（快、直观）、-c 10 抓 10 个自动停、-w xx.pcap 存文件（可以拷到 Windows 用 Wireshark 打开分析——你的 Wireshark 功底在这里接上）。

任务 4：mtr 与 nc（20 分钟）
bash
sudo dnf install -y mtr nc
mtr -n 223.5.5.5           # ping+tracert 合体，逐跳看丢包（Ctrl+C 退出）
nc -zv 127.0.0.1 22        # 测端口通不通：succeeded!
nc -zv 127.0.0.1 9999      # 不通的样子：Connection refused
nc -zv 是"端口版 ping"——ping 通不代表端口通，这个区别你以后天天用。

任务 5：笔记 + 打卡（10 分钟）
notes/day12.md 要点：ip/ss 命令与 display 对照表；三次握手抓包截图或文字记录；nc -zv 与 ping 的区别；127.0.0.1 vs 0.0.0.0 监听地址的理解。
bash
cd ~/code/neteng-to-sre
git add . && git commit -m "Day 12: 网络排障工具箱"
gtest && git push

2.测试输出
[kxwang@localhost day12]$ ip addr
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo
       valid_lft forever preferred_lft forever
    inet6 ::1/128 scope host 
       valid_lft forever preferred_lft forever
2: ens160: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc mq state UP group default qlen 1000
    link/ether 00:0c:29:0e:67:5a brd ff:ff:ff:ff:ff:ff
    altname enp3s0
    inet 192.168.30.134/24 brd 192.168.30.255 scope global dynamic noprefixroute ens160
       valid_lft 1383sec preferred_lft 1383sec
    inet6 fe80::20c:29ff:fe0e:675a/64 scope link noprefixroute 
       valid_lft forever preferred_lft forever
3: ens192: <NO-CARRIER,BROADCAST,MULTICAST,UP> mtu 1500 qdisc mq state DOWN group default qlen 1000
    link/ether 00:0c:29:0e:67:64 brd ff:ff:ff:ff:ff:ff
    altname enp11s0
[kxwang@localhost day12]$ ip route
default via 192.168.30.2 dev ens160 proto dhcp src 192.168.30.134 metric 100 
192.168.30.0/24 dev ens160 proto kernel scope link src 192.168.30.134 metric 100 
[kxwang@localhost day12]$ ip -s link
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN mode DEFAULT group default qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    RX:  bytes packets errors dropped  missed   mcast           
      88507412  967501      0       0       0       0 
    TX:  bytes packets errors dropped carrier collsns           
      88507412  967501      0       0       0       0 
2: ens160: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc mq state UP mode DEFAULT group default qlen 1000
    link/ether 00:0c:29:0e:67:5a brd ff:ff:ff:ff:ff:ff
    RX:  bytes packets errors dropped  missed   mcast           
     618448437  863326      0       0       0       0 
    TX:  bytes packets errors dropped carrier collsns           
      60765079  600771      0       0       0       0 
    altname enp3s0
3: ens192: <NO-CARRIER,BROADCAST,MULTICAST,UP> mtu 1500 qdisc mq state DOWN mode DEFAULT group default qlen 1000
    link/ether 00:0c:29:0e:67:64 brd ff:ff:ff:ff:ff:ff
    RX:  bytes packets errors dropped  missed   mcast           
             0       0      0       0       0       0 
    TX:  bytes packets errors dropped carrier collsns           
             0       0      0       0       0       0 
    altname enp11s0
[kxwang@localhost day12]$ ip route get 223.5.5.5
223.5.5.5 via 192.168.30.2 dev ens160 src 192.168.30.134 uid 1000 
    cache 

[kxwang@localhost day12]$ ss -tlnp
State                                Recv-Q                               Send-Q                                                             Local Address:Port                                                              Peer Address:Port                              Process                                                       
LISTEN                               0                                    128                                                                      0.0.0.0:22                                                                     0.0.0.0:*                                                                                               
LISTEN                               0                                    511                                                                    127.0.0.1:33289                                                                  0.0.0.0:*                                  users:(("node",pid=2014,fd=18))                              
LISTEN                               0                                    4096                                                                   127.0.0.1:631                                                                    0.0.0.0:*                                                                                               
LISTEN                               0                                    511                                                                    127.0.0.1:40303                                                                  0.0.0.0:*                                  users:(("node",pid=2144,fd=18))                              
LISTEN                               0                                    128                                                                         [::]:22                                                                        [::]:*                                                                                               
LISTEN                               0                                    4096                                                                       [::1]:631                                                                       [::]:*                                                                                               
[kxwang@localhost day12]$ ss -tnp state established
Recv-Q                                   Send-Q                                                                        Local Address:Port                                                                         Peer Address:Port                                    Process                                                            
0                                        0                                                                                 127.0.0.1:40303                                                                           127.0.0.1:43410                                    users:(("node",pid=2796,fd=24))                                   
0                                        0                                                                            192.168.30.134:22                                                                           192.168.30.1:58272                                                                                                      
0                                        0                                                                                 127.0.0.1:40303                                                                           127.0.0.1:43408                                    users:(("node",pid=2144,fd=21))                                   
0                                        0                                                                            192.168.30.134:59728                                                                       52.86.219.133:443                                      users:(("node",pid=2796,fd=47))                                   
0                                        24                                                                                127.0.0.1:43408                                                                           127.0.0.1:40303                                                                                                      
0                                        23                                                                                127.0.0.1:43410                                                                           127.0.0.1:40303                                                                                                      
[kxwang@localhost day12]$ ss -tlnp | grep :22
LISTEN 0      128          0.0.0.0:22         0.0.0.0:*                                   
LISTEN 0      128             [::]:22            [::]:*                                   
[kxwang@localhost day12]$ ss -s
Total: 569
TCP:   12 (estab 5, closed 1, orphaned 0, timewait 1)

Transport Total     IP        IPv6
RAW       1         0         1        
UDP       5         3         2        
TCP       11        9         2        
INET      17        12        5        
FRAG      0         0         0 

tcpdump: data link type LINUX_SLL2
dropped privs to tcpdump
tcpdump: verbose output suppressed, use -v[v]... for full protocol decode
listening on any, link-type LINUX_SLL2 (Linux cooked v2), snapshot length 262144 bytes
15:28:04.878440 lo    In  IP 127.0.0.1 > 127.0.0.1: ICMP echo request, id 10, seq 1, length 65
15:28:04.878453 lo    In  IP 127.0.0.1 > 127.0.0.1: ICMP echo reply, id 10, seq 1, length 66
15:28:05.909272 lo    In  IP 127.0.0.1 > 127.0.0.1: ICMP echo request, id 10, seq 2, length 64
15:28:05.909289 lo    In  IP 127.0.0.1 > 127.0.0.1: ICMP echo reply, id 10, seq 2, length 64
15:28:06.934964 lo    In  IP 127.0.0.1 > 127.0.0.1: ICMP echo request, id 10, seq 3, length 64
15:28:06.934979 lo    In  IP 127.0.0.1 > 127.0.0.1: ICMP echo reply, id 10, seq 3, length 64

[kxwang@localhost day12]$ sudo tcpdump -i lo tcp port 22 -nn
dropped privs to tcpdump
tcpdump: verbose output suppressed, use -v[v]... for full protocol decode
listening on lo, link-type EN10MB (Ethernet), snapshot length 262144 bytes
15:29:02.471775 IP 127.0.0.1.41032 > 127.0.0.1.22: Flags [S], seq 1586803311, win 65495, options [mss 65495,sackOK,TS val 2387368387 ecr 0,nop,wscale 7], length 0
15:29:02.471790 IP 127.0.0.1.22 > 127.0.0.1.41032: Flags [S.], seq 2243324730, ack 1586803312, win 65483, options [mss 65495,sackOK,TS val 2387368387 ecr 2387368387,nop,wscale 7], length 0
15:29:02.471799 IP 127.0.0.1.41032 > 127.0.0.1.22: Flags [.], ack 1, win 512, options [nop,nop,TS val 2387368387 ecr 2387368387], length 0
15:29:02.472037 IP 127.0.0.1.41032 > 127.0.0.1.22: Flags [P.], seq 1:22, ack 1, win 512, options [nop,nop,TS val 2387368387 ecr 2387368387], length 21: SSH: SSH-2.0-OpenSSH_8.7
15:29:02.472046 IP 127.0.0.1.22 > 127.0.0.1.41032: Flags [.], ack 22, win 512, options [nop,nop,TS val 2387368387 ecr 2387368387], length 0
15:29:02.479168 IP 127.0.0.1.22 > 127.0.0.1.41032: Flags [P.], seq 1:22, ack 22, win 512, options [nop,nop,TS val 2387368394 ecr 2387368387], length 21: SSH: SSH-2.0-OpenSSH_8.7
15:29:02.479186 IP 127.0.0.1.41032 > 127.0.0.1.22: Flags [.], ack 22, win 512, options [nop,nop,TS val 2387368394 ecr 2387368394], length 0
15:29:02.479397 IP 127.0.0.1.41032 > 127.0.0.1.22: Flags [P.], seq 22:1414, ack 22, win 512, options [nop,nop,TS val 2387368395 ecr 2387368394], length 1392
15:29:02.480282 IP 127.0.0.1.22 > 127.0.0.1.41032: Flags [P.], seq 22:990, ack 1414, win 522, options [nop,nop,TS val 2387368395 ecr 2387368395], length 968
15:29:02.481178 IP 127.0.0.1.41032 > 127.0.0.1.22: Flags [P.], seq 1414:1462, ack 990, win 505, options [nop,nop,TS val 2387368396 ecr 2387368395], length 48
15:29:02.483008 IP 127.0.0.1.22 > 127.0.0.1.41032: Flags [P.], seq 990:1474, ack 1462, win 522, options [nop,nop,TS val 2387368398 ecr 2387368396], length 484
15:29:02.485201 IP 127.0.0.1.41032 > 127.0.0.1.22: Flags [P.], seq 1462:1478, ack 1474, win 502, options [nop,nop,TS val 2387368400 ecr 2387368398], length 16
15:29:02.530059 IP 127.0.0.1.22 > 127.0.0.1.41032: Flags [.], ack 1478, win 522, options [nop,nop,TS val 2387368445 ecr 2387368400], length 0
15:29:02.530076 IP 127.0.0.1.41032 > 127.0.0.1.22: Flags [P.], seq 1478:1530, ack 1474, win 502, options [nop,nop,TS val 2387368445 ecr 2387368445], length 52
15:29:02.530095 IP 127.0.0.1.22 > 127.0.0.1.41032: Flags [.], ack 1530, win 522, options [nop,nop,TS val 2387368445 ecr 2387368445], length 0
15:29:02.530184 IP 127.0.0.1.22 > 127.0.0.1.41032: Flags [P.], seq 1474:1526, ack 1530, win 522, options [nop,nop,TS val 2387368445 ecr 2387368445], length 52
15:29:02.530244 IP 127.0.0.1.41032 > 127.0.0.1.22: Flags [P.], seq 1530:1598, ack 1526, win 502, options [nop,nop,TS val 2387368445 ecr 2387368445], length 68
15:29:02.531019 IP 127.0.0.1.22 > 127.0.0.1.41032: Flags [P.], seq 1526:1610, ack 1598, win 522, options [nop,nop,TS val 2387368446 ecr 2387368445], length 84
15:29:02.575411 IP 127.0.0.1.41032 > 127.0.0.1.22: Flags [.], ack 1610, win 502, options [nop,nop,TS val 2387368491 ecr 2387368446], length 0
15:29:06.602590 IP 127.0.0.1.41032 > 127.0.0.1.22: Flags [P.], seq 1598:1746, ack 1610, win 502, options [nop,nop,TS val 2387372518 ecr 2387368446], length 148
15:29:06.616915 IP 127.0.0.1.22 > 127.0.0.1.41032: Flags [P.], seq 1610:1646, ack 1746, win 527, options [nop,nop,TS val 2387372532 ecr 2387372518], length 36
15:29:06.616938 IP 127.0.0.1.41032 > 127.0.0.1.22: Flags [.], ack 1646, win 502, options [nop,nop,TS val 2387372532 ecr 2387372532], length 0
15:29:06.617020 IP 127.0.0.1.41032 > 127.0.0.1.22: Flags [P.], seq 1746:1866, ack 1646, win 502, options [nop,nop,TS val 2387372532 ecr 2387372532], length 120
15:29:06.661272 IP 127.0.0.1.22 > 127.0.0.1.41032: Flags [.], ack 1866, win 527, options [nop,nop,TS val 2387372576 ecr 2387372532], length 0
15:29:06.699362 IP 127.0.0.1.22 > 127.0.0.1.41032: Flags [P.], seq 1646:2274, ack 1866, win 527, options [nop,nop,TS val 2387372614 ecr 2387372532], length 628
15:29:06.738962 IP 127.0.0.1.41032 > 127.0.0.1.22: Flags [.], ack 2274, win 498, options [nop,nop,TS val 2387372654 ecr 2387372614], length 0
15:29:06.738995 IP 127.0.0.1.22 > 127.0.0.1.41032: Flags [P.], seq 2274:2326, ack 1866, win 527, options [nop,nop,TS val 2387372654 ecr 2387372654], length 52
15:29:06.739015 IP 127.0.0.1.41032 > 127.0.0.1.22: Flags [.], ack 2326, win 498, options [nop,nop,TS val 2387372654 ecr 2387372654], length 0
15:29:06.739218 IP 127.0.0.1.41032 > 127.0.0.1.22: Flags [P.], seq 1866:1918, ack 2326, win 498, options [nop,nop,TS val 2387372654 ecr 2387372654], length 52
15:29:06.739240 IP 127.0.0.1.22 > 127.0.0.1.41032: Flags [.], ack 1918, win 527, options [nop,nop,TS val 2387372654 ecr 2387372654], length 0
15:29:06.740514 IP 127.0.0.1.22 > 127.0.0.1.41032: Flags [P.], seq 2326:2398, ack 1918, win 527, options [nop,nop,TS val 2387372656 ecr 2387372654], length 72
15:29:06.766454 IP 127.0.0.1.22 > 127.0.0.1.41032: Flags [P.], seq 2398:2574, ack 1918, win 527, options [nop,nop,TS val 2387372682 ecr 2387372654], length 176
15:29:06.766499 IP 127.0.0.1.41032 > 127.0.0.1.22: Flags [.], ack 2574, win 497, options [nop,nop,TS val 2387372682 ecr 2387372656], length 0
15:29:06.766540 IP 127.0.0.1.41032 > 127.0.0.1.22: Flags [P.], seq 1918:1954, ack 2574, win 497, options [nop,nop,TS val 2387372682 ecr 2387372656], length 36
15:29:06.766560 IP 127.0.0.1.41032 > 127.0.0.1.22: Flags [P.], seq 1954:2022, ack 2574, win 497, options [nop,nop,TS val 2387372682 ecr 2387372656], length 68
15:29:06.766574 IP 127.0.0.1.41032 > 127.0.0.1.22: Flags [F.], seq 2022, ack 2574, win 497, options [nop,nop,TS val 2387372682 ecr 2387372656], length 0
15:29:06.766606 IP 127.0.0.1.22 > 127.0.0.1.41032: Flags [.], ack 2023, win 527, options [nop,nop,TS val 2387372682 ecr 2387372682], length 0
15:29:06.769670 IP 127.0.0.1.22 > 127.0.0.1.41032: Flags [F.], seq 2574, ack 2023, win 527, options [nop,nop,TS val 2387372685 ecr 2387372682], length 0
15:29:06.769685 IP 127.0.0.1.41032 > 127.0.0.1.22: Flags [.], ack 2575, win 497, options [nop,nop,TS val 2387372685 ecr 2387372685], length 0

3.验收
(1)ss -tlnp 每个字母的含义？
答:t=TCP、I=监听中、n=数字显示(不解析域名/端口名)、p=显示占用进程。

(2)TCP 三次握手的三个包标志位依次是什么？
答:SYN[S] → SYN-ACK[S.] → ACK[.]

(3)tcpdump 里 -nn 的作用？抓包存文件给 Wireshark 分析用哪个选项？
答:-nn不解析主机名和端口名(显示纯IP和数字端口、更快更直观)；存文档用-w文件.pcap，拷出来给Wireshark分析。

(4)测试对端 443 端口通不通用什么命令？为什么 ping 通不算数？
答:nc -zv对端IP 443。ping只验证三层可达(ICMP),端口不通是四层的事--防火墙可能放行ICMP但拦TCP 443，所以ping通不算数。

(5)"服务不通"的分层排查顺序是什么？（提示：进程活着→在监听→监听地址→防火墙→网络可达）
答:自内向外逐层排:进程活着(systemctl status) → 在监听(ss -tlnp) → 监听地址对不对(127.0.0.1还是0.0.0.0) → 本机防火墙(nftables/安全组) → 网络可达性(ping/mtr/nc)














