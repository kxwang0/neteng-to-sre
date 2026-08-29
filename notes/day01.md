Day1:文件系统与基本命令
1.今天学到的命令
whoami		#我是谁
hostname	#我在哪台机器上
pwd		#我在哪个目录
sudo dnf install -y tree	#装个目录树工具

cd /		#去根目录
ls		#看一级目录
tree -L 1 /	#树状显示一级目录（更直观）

cat /proc/cpuinfo | head -20	#CPU信息
cat /proc/meminfo | head -5	#内存信息
uptime				#负载

cd ~				#回家目录
mkdir -p ~/practice/{a,b,c}	#一次建三个目录，体会花括号展开
ls practice/			#看practice/下文件
touch practice/a/test1.txt	#建空文件
echo "hello linux" > practice/a/test2.txt	#建带内容的文件(>是重定向)
cat practice/a/test2.txt	#看内容
cp practice/a/test1.txt practice/b/	#复制
cp -r practice/a practice/c/a_backup	#复制整个目录要加-r 
mv practice/b/test1.txt practice/b/renamed.txt	#同目录 mv = 改名
mv practice/b/renamed.txt practice/c/		#跨目录 mv = 移动
rm practice/c/renamed.txt			#删除文件
rm -r practice/c/a_backup			#删除目录要加-r
ls -l practice/a/				#详细信息
ls -la ~					#-a显示隐藏文件(.开头的)
ls -lh /etc/ | head				#-h 让人类可读大小

rm -rf/某目录，没有回收站，不问确认，直接删除，严重警告风险操作

cd /etc			#绝对路径：以/开头，走到哪里都不会迷路
cd  ~/practice		#~开头的路径
cd a			#相对路径：相对于当前位置
cd ..			#上一级
cd ../..		#上两级
cd -			#回到上一次所在的目录

2.目录结构图
/etc			#所有配置文件
/var/log		#日志文件
/home			#普通用户家目录
/root			#root的家目录
/usr			#安装的软件
/opt			#第三方软件
/tmp			#临时文件(重启清空)
/proc			#系统实时运行状态(虚拟文件)
/dev			#设备文件
/bin			#命令程序
/sbin			#命令程序

3.验收
(1)/etc、/var/log、/home、/opt、/proc 各放什么？
答：/etc所有配置文件、/var/log日志文件、/home普通用户家目录、/proc系统实时运行状态

(2)绝对路径和相对路径的区别？cd - 是干什么的？
答：绝对路径固定不变，任何位置都能用，相对路径依赖pwd，换目录就失效，cd - 是回到上一次所在目录

(3)为什么 rm -rf 要格外小心？
答：没有回收站，不问确认，直接删除

(4)怎么查一个陌生命令的用法？
答：man -ls进入手册

(5)ls -l 输出第一列 -rw-r--r-- 大概是什么意思？
答：读写权限



