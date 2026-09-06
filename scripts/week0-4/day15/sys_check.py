# sys_check.py
import subprocess       #调用系统命令的标准库

def run(cmd):           #定义函数:执行命令并返回输出文本
    result = subprocess.run(cmd,shell=True,capture_output=True,text=True)
    return result.stdout

def main():
    print("=====系统巡检报告(python版)=====")
    print("---负载---");        print(run("uptime"))
    print("---内存---");        print(run("free -h"))
    print("---磁盘---");        print(run("df -h /"))
    print("---监听端口---");    print(run("ss -tln"))

if __name__ == "__main__":  #Python脚本的"主入口"固定写法
    main()
