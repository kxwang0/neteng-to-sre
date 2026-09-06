1.今日学习内容
Day 11 详细手册：网络命名空间——容器网络的微观模型（约 2 小时）
今天是你网络功底直接变现的一天。network namespace 就是 Linux 里的"VRF"，veth pair 就是"网线"——你拿路由交换的知识框架套上去，瞬间就懂。

任务 0：GitHub 自测 + 热身（5 分钟）
bash
gtest
ip netns list        # 现在应该是空的

任务 1：概念映射（10 分钟）
表格
Linux 概念	网工类比
network namespace	VRF 实例（独立的接口、路由表、防火墙规则）
veth pair	一根网线的两头（成对存在，一进一出）
ip netns exec r1 命令	进入某台"设备"的视图执行命令
宿主机的 root namespace	全局路由表/默认 VRF

任务 2：实战——建两个"路由器"直连互 ping（45 分钟）
bash
# 1. 建两个命名空间（= 两台独立设备）
sudo ip netns add r1
sudo ip netns add r2
ip netns list

# 2. 创建 veth pair（= 一根网线）
sudo ip link add veth-r1 type veth peer name veth-r2
ip link show | grep veth          # 现在两头都在宿主机上

# 3. 把网线两头分别插进两台设备
sudo ip link set veth-r1 netns r1
sudo ip link set veth-r2 netns r2
ip link show | grep veth          # 宿主机上看不到了——被"插"走了

# 4. 配 IP（用 /30 互联地址，和行业实践一致）
sudo ip netns exec r1 ip addr add 10.0.0.1/30 dev veth-r1
sudo ip netns exec r2 ip addr add 10.0.0.2/30 dev veth-r2

# 5. 拉起接口（两个都要：lo 和业务口——新 netns 里接口默认 DOWN）
sudo ip netns exec r1 ip link set lo up
sudo ip netns exec r1 ip link set veth-r1 up
sudo ip netns exec r2 ip link set lo up
sudo ip netns exec r2 ip link set veth-r2 up

# 6. 验证连通性
sudo ip netns exec r1 ping -c 3 10.0.0.2
排障视角观察（都是老本行）：
bash
sudo ip netns exec r1 ip addr                 # ≈ display ip interface brief
sudo ip netns exec r1 ip route                # ≈ display ip routing-table
sudo ip netns exec r1 arp -n                  # ≈ display arp（ping 通后能看到对端 MAC）

任务 3：抓包看一眼 ARP 真容（25 分钟，Day 12 预告）
bash
# 终端 A：在 r1 上抓包
sudo ip netns exec r1 tcpdump -i veth-r1 -nn

# 终端 B：先清 ARP 再 ping，观察完整的 ARP 请求/应答 + ICMP 过程
sudo ip netns exec r1 arp -d 10.0.0.2
sudo ip netns exec r1 ping -c 2 10.0.0.2
在终端 A 你应该依次看到：ARP, Request who-has → ARP, Reply → ICMP echo request/reply——这就是你讲过的"先 ARP 后 ICMP"，现在在 Linux 里亲眼看到。

任务 4：清理 + 笔记打卡（15 分钟）
bash
sudo ip netns del r1
sudo ip netns del r2
ip netns list                     # 确认清理干净

notes/day11.md 要点：netns/veth 与 VRF/网线的类比表；为什么接口要手动 set up（含 lo）；ARP 抓包观察记录；为什么这是容器网络的微观模型（Docker 容器 = 进程 + namespace，K8s Pod 之间的通信底层就是这套）。
bash
cd ~/code/neteng-to-sre
git add . && git commit -m "Day 11: network namespace实战"
gtest && git push

2.验收
(1)network namespace 相当于网工世界里的什么？
答:VRF实例--独立的接口、路由表、防火墙规则，彼此隔离。

(2)veth pair 相当于什么？为什么创建时必须成对？
答:一根网线的两头；veth是虚拟以太网卡，数据从一头进必然从另一头出，单头没有意义，所以必须成对创建。

(3)新 namespace 里接口默认是什么状态？要拉起哪两个接口？
答:默认全部DOWN；要拉起lo(环回口,不拉起连127.0.0.1都不通)和业务口veth-rx两个

(4)ip netns exec r1 ping ... 中 exec 的作用？
答:exec表示"在指定命名空间里执行后面的命令"--相当于进入那台设备的视图敲命令

(5)Docker 容器和这个实验的关系是什么？
答:Docker容器的网络隔离就是基于network namespace实现的;每个容器=一个netns，容器互联=veth pair + 网桥，今天的实验就是容器网络的手工版微观模型--以后排查K8s Pod网络问题，底层就是这套



