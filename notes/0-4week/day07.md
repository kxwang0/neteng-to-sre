今天把第 2–4 个月要用的"武器库"一次备齐，并写出人生第一个 Netmiko 脚本。之后进入第 2 周 Shell 脚本特训。

任务 0：GitHub 自测 + 热身（5 分钟）
bash
gtest
python3.12 --version    # 确认昨天的成果还在

任务 1：安装全套网络自动化库（25 分钟）
bash
# 用国内源加速（前提是 Day 6 的 ssl 验证通过）
python3.12 -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple \
  ansible-core netmiko nornir nornir-netmiko nornir-utils \
  napalm scrapli paramiko ncclient textfsm \
  jinja2 pyyaml requests urllib3

# 加密底座（paramiko/netmiko 的算法支撑，单独装一遍防漏）
python3.12 -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple \
  cryptography pyasn1 pynacl bcrypt

# ansible 命令做个软链，方便直接敲
sudo ln -sf /usr/local/python3.12/bin/ansible /usr/local/bin/ansible

安装时认识一下你的武器（每个库管什么，验收要考）：
表格
库	定位	网工一句话理解
netmiko	SSH 连设备执行命令	脚本版的 SecureCRT 批量登录
paramiko	底层 SSH 协议库	netmiko 的地基
nornir	批量并发框架	同时操作几百台设备的调度器
napalm	跨厂商统一 API	华为/思科/ juniper 用同一套代码操作
scrapli	新一代 SSH 库	netmiko 的现代替代品
ncclient	NETCONF 协议	走 XML 的结构化设备管理
textfsm	文本解析模板	把 display 输出变成结构化表格
ansible-core	自动化引擎	第 3 个月的主角
jinja2 / pyyaml / requests	模板 / YAML / HTTP	通用工具库

任务 2：逐个验证（10 分钟）
bash
for m in ansible netmiko nornir napalm scrapli paramiko ncclient textfsm; do
  python3.12 -c "import $m; print('$m', getattr($m,'__version__','?'))"
done
全部打印出版本号才算过。哪个报错就用 python3.12 -m pip install 库名 单独补装。

任务 3：人生第一个 Netmiko 冒烟脚本（30 分钟）
还没接模拟器/真设备也没关系——用 Netmiko 连你自己的 Rocky 本机，先把"SSH 连接 → 执行命令 → 拿返回"的完整链路跑通：
bash
mkdir -p ~/code/neteng-to-sre/scripts && cd ~/code/neteng-to-sre/scripts
vim netmiko_smoke.py
Python
from netmiko import ConnectHandler

# device_type 用 linux：把本机当一台"设备"连
dev = {
    "device_type": "linux",
    "host": "127.0.0.1",
    "username": "kxwang",
    "password": "你的登录密码",
}

conn = ConnectHandler(**dev)
output = conn.send_command("hostname && uptime")
print("===== 设备返回 =====")
print(output)
conn.disconnect()
bash
python3.12 netmiko_smoke.py
看到打印出主机名和 uptime，说明整条链路（SSH 认证 → 下发命令 → 回显采集）全通了——将来把 host 换成设备管理 IP、device_type 换成 huawei/hp_comware，就是真正的网络自动化。

任务 4：第 1 周复盘（20 分钟）
新建 notes/week01-review.md，回答三个问题：

任务 5：关机打快照（5 分钟）
bash
sudo poweroff
到 VMware 里对虚拟机打快照，命名 01-开发环境就绪——这意味着就算后面玩坏了，也能一键回到"Python 3.12 + 全套库"的今天。
开机后打卡：
bash
cd ~/code/neteng-to-sre
git add . && git commit -m "Day 7: 自动化库成军 + 第1周复盘"
gtest && git push

2.验收
(1)netmiko、nornir、napalm 三者的定位区别？
答:netmiko是SSH连设备执行命令，nornir是批量并发框架，napalm是跨厂商统一API

(2)为什么装库要用 python3.12 -m pip 而不是裸 pip？（提示：系统还有 3.9 的 pip，装错解释器等于白装）
答:因为后续要使用python3.12完成后续任务，如果不带python3.12 -m pip那么就会安装到python3.9的目录上面

(3)textfsm 解决什么问题？
答:把设备display / show命令的纯本文回显解析成结构化数据
设备输出是给人看的，比如：
plain
GE0/0/1   up    up     10.1.1.1
GE0/0/2   down  down   --
人眼能看懂，但程序没法直接用。textfsm 按模板把每行变成字典：{"interface": "GE0/0/1", "phy": "up", "protocol": "up", "ip": "10.1.1.1"}——之后脚本就能精确取 ip 字段做判断、存数据库、出报表。一句话：它把"人看的回显"变成"程序能用的数据"，是网络自动化里"采集→解析"环节的核心工具（第 2 个月的项目会大量用它）。

(4)怎么确认某个库到底装没装、装的哪个版本？（python3.12 -m pip show netmiko）
答:python3.12 -m pip show netmiko 装了 → 显示 Name、Version、Location（装在哪）；没装 → 提示 WARNING: Package(s) not found。想看全部家当：python3.12 -m pip list。

(5)冒烟脚本里 device_type 的作用是什么？换成华为设备该填什么？
答:device_type 是告诉 Netmiko 对端是什么系统——因为不同厂商设备的"脾气"完全不同：登录后提示符长什么样（<Huawei> 还是 R1>）、分页怎么处理（华为的 ---- More ---- vs 思科的 --More--）、命令回显格式差异。Netmiko 内部按 device_type 选对应的"驱动"来处理这些差异。
华为："huawei"
H3C："hp_comware"
思科："cisco_ios"
这就是为什么冒烟脚本里填 "linux" 能连 Rocky——Netmiko 也有 Linux 的驱动。将来接模拟器里的华为设备，改两个字段就能用：host 换成设备管理 IP，device_type 换成 "huawei"。
