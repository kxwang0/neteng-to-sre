# 任务写在终端里。从下一行开始敲，不要粘贴手册。
# 写好保存，回到终端按回车批改。

def demo(**kwargs):
    print(kwargs)

d = {"host":"1.1.1.1","username":"netops"}
demo(**d)
demo(host="1.1.1.1",username="netops")
