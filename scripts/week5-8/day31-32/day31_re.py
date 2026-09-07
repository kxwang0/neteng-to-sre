import re

text = "GigabitEthernet0/0/1     up    up     192.168.1.1"

# 注意：写成脚本后，表达式算完就丢掉了，屏幕上看不到。
# 交互模式（python3.12 进 >>>）会自动回显；python3.12 day31_re.py 不会。
# 要看到结果，必须 print(...)

print(re.search(r"\d+\.\d+\.\d+\.\d+", text))   # 第一个 IP，返回 Match 对象（不是列表）
print(re.findall(r"up|down", text))             # 所有 up/down，返回列表

m = re.search(r"^(\S+)\s+(up|down)", text)      # () 分组：圈出要抠的部分
print(m.group(0))  # 整个匹配到的内容
print(m.group(1))  # 第一个括号，接口名称
print(m.group(2))  # 第二个括号，物理状态
