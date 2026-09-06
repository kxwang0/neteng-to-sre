# ping_result.py:遍历设备清单，打印巡检结论(纯逻辑版，真ping在Day17)
devices = ["192.168.1.1","192.168.1.2","192.168.1.3"]
for ip in devices:          #for 循环(注意缩进4空格,这是Python的命)
    print(f"正在检查 {ip} ...")

for i in range(3):          #range(3) = 0,1,2
    print("第", i + 1, "轮")

status = "up"
if status == "up":          #if判断(结尾冒号别丢)
    print("接口正常")
elif status == "down":
    print("接口故障")
else:
    print("未知状态")

count = 0
while count < 3:            #while循环
    print("重试第",count + 1, "次")
    count += 1              #Python没有count++
