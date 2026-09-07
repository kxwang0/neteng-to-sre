def demo(**kwargs):
    print(kwargs)

demo(host="1.1.1.1",username="netops")      #打印出的就是字典
d = {"host":"1.1.1.1","username":"netops"}
demo(**d)                                 #和上面完全等价