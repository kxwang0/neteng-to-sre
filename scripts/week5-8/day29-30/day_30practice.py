# Day 30 练习：把 Day 24 的「一条龙脚本」拆成两个函数
#
# 结构对照（从上到下读）：
#   1. import          —— 引入别人写好的能力
#   2. def collect     —— 零件 A：连设备、跑命令、把结果装进字典返回
#   3. def save_report —— 零件 B：把字典写进文本文件
#   4. if __name__     —— 组装线：只有「直接 python 跑这个文件」时才执行
#
# 相对 Day 24 的进步：采集和写文件解耦了。
#   以后换设备、换命令、换文件名，只改最下面几行，两个函数不用动。

from netmiko import ConnectHandler   # SSH 连网络设备、发 CLI 命令
from getpass import getpass          # 运行时交互输入密码，不把密码写进代码
from datetime import datetime        # 取本机当前时间，用来拼进文件名


def collect(host, username, password, commands, device_type="huawei"):
    """连接一台设备，批量执行命令，返回 {命令字符串: 设备输出} 字典。

    参数（调用时按位置或按名字传都行）：
      host         设备 IP，例如 "192.168.30.252"
      username     登录用户名
      password     登录密码（主程序里用 getpass 拿到再传进来）
      commands     命令列表，例如 ["display version", "display device"]
      device_type  Netmiko 平台名；华为 VRP 用 "huawei"，这是默认值，可省略

    返回值不是打印到屏幕，而是 return 给调用方，方便后面再写文件 / 再处理。
    """
    # Netmiko 要的是「连接参数字典」。键名必须是它认识的：host / username / ...
    # 这里用函数参数填字典，而不是把 IP、账号写死在函数里——函数才能复用。
    dev = {
        "host": host,
        "username": username,
        "password": password,
        "device_type": device_type,
    }

    result = {}                      # 空字典，循环里往里面塞「命令 → 输出」
    conn = ConnectHandler(**dev)     # ** 把字典拆成关键字参数，等价于
                                     # ConnectHandler(host=..., username=..., ...)
                                     # SSH 会话很贵：整个函数只连一次
    for cmd in commands:             # 遍历命令列表，每条发一次、收一次
        result[cmd] = conn.send_command(cmd)  # 键=命令，值=设备回显字符串
    conn.disconnect()                # 用完立刻断开，释放设备侧会话
    return result                    # 把整本「命令账本」交还给调用方


def save_report(data, filename):
    """把 collect() 返回的字典写成一份汇总文本。

    data     形如 {"display version": "Huawei VRP ...", "display device": "..."}
    filename 要写入的文件名，例如 "R1_采集汇总.txt"
    """
    # "w" = 覆盖写：每次跑都生成新文件，旧内容丢掉
    # with：离开这个缩进块就自动关文件，中途报错也会关
    with open(filename, "w") as f:
        for cmd, output in data.items():          # .items() 一次取出「键, 值」
            f.write(f"====={cmd}=====\n{output}\n\n")
            # =====display version=====     ← 分隔标题，事后 grep 能按命令跳
            # <设备原始输出>
            # <空行，和下一条命令隔开>


# ---------------------------------------------------------------------------
# 下面才是「真正跑起来」的入口。
#
# 直接执行：python day_30practice.py  →  __name__ 等于 "__main__"，会跑这里
# 被别人 import：from day_30practice import collect  →  只加载函数，不连设备
# 这就是为什么采集逻辑要放进函数、启动逻辑要放进这个 if 里。
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # 1) 这次巡检要跑哪些命令（列表，顺序就是执行顺序）
    cmds = ["display version", "display device", "display interface brief"]

    # 2) 调用零件 A：连 192.168.30.252，用 admin1 + 终端输入的密码，跑 cmds
    #    getpass(...) 会先暂停，等你输入密码（屏幕不回显），再把字符串传给 collect
    data = collect("192.168.30.252", "admin1", getpass("输入设备密码: "), cmds)

    # 3) 用「跑脚本这一刻」的本地时间拼文件名，每次运行一份新文件，旧的不会被覆盖
    #    strftime 是把 datetime 格式化成字符串；文件名里不能用冒号，所以用 20260907_000312 这种
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"R1_采集汇总_{stamp}.txt"
    save_report(data, filename)

    print(f"完成，已写入 {filename}")
