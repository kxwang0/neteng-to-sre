# 练习:解析/etc/passwd,输出用户名和"shell"对照表
with open("/etc/passwd","r") as f:      #with打开;用完自动关闭
    for line in f:
        line = line.strip()
        if not line:
            continue
        parts = line.split(":")         #按冒号切割(想想awk -F:)
        print(parts[0],parts[6])

#写入文件
with open("output.txt","w") as f:       #"w"覆盖写，"a"追加写
    f.write("第一行\n")