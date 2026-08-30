Day2文件查看与权限
1.学到的命令
cd ~ && pwd	#到家目录，成功输出pwd路径
whoami && id	#id会显示你的uid、所属组，注意看有没有wheel组

cat /etc/hostname			#小文件一口气看完
cat /var/log/messages | head -30	#大文件别直接cat，会刷屏
head -20 /var/log/messages		#看开头20行
tail -20 /var/log/messages		#看结尾20行
less /var/log/messages			#分页查看：方向键翻页、/关键词搜索、q退出
wc -l /var/log/messages			#统计行数

sudo tail -f /var/log/secure		#实时盯SSH登录日志，终端会"停"在这里，类似于网络设备的terminal monitor

mkdir /tmp/permtest && cd /tmp/permtest
echo "机密配置" > secret.txt
echo 'echo hello world' > hello.sh
ls -l

逐列看懂输出（以 -rw-r--r-- 1 kxwang kxwang 5 ... secret.txt 为例）：
plain
-        rw-       r--       r--     1  kxwang  kxwang   5   ...  secret.txt
│         │         │         │      │     │       │      │         └ 文件名
│         │         │         │      │     │       │      └ 大小(字节)
│         │         │         │      │     │       └ 属组
│         │         │         │      │     └ 属主
│         │         │         │      └ 硬链接数
│         │         │         └ 其他人(other)权限：只读
│         │         └ 同组人(group)权限：只读
│         └ 属主(user)权限：读+写
└ 文件类型：-普通文件 d目录 l链接

权限数字口诀：r=4，w=2，x=1，加起来就是一位：
表格
数字	计算	含义	典型场景
644	6=4+2, 4, 4	属主读写，其他人只读	普通文件、网页文件
600	6=4+2, 0, 0	只有属主能读写	私钥、密码文件（~/.ssh/id_ed25519 就是它）
755	7=4+2+1, 5=4+1, 5	属主全能，其他人读+执行	脚本、程序、目录
700	7, 0, 0	只有属主能进	私密目录（~/.ssh 就是它）

实验一：执行权限。直接运行脚本会报 Permission denied，加 x 后成功——chmod +x 是以后天天用的命令：
bash
./hello.sh                 # 拒绝：没有执行权限
chmod +x hello.sh          # 等于 chmod 755
./hello.sh                 # hello world
实验二：600 文件别人读不到。建一个测试用户，用他的眼睛看你的文件（这里用 /tmp/permtest 做实验，因为 Rocky 的家目录默认 700，别人本来就进不来）：
bash
sudo useradd -m tester && echo 'tester:Test@123' | sudo chpasswd   # 建个测试账号
chmod 644 secret.txt
su - tester -c 'cat /tmp/permtest/secret.txt'     # 能读到：机密配置
chmod 600 secret.txt
su - tester -c 'cat /tmp/permtest/secret.txt'     # Permission denied！
实验三：目录的 x 权限 = 门禁。把目录改成 700，即使里面的文件是 644，别人照样进不来——目录的 x 决定能不能 cd 进去，r 决定能不能 ls 看内容：
bash
chmod 644 secret.txt          # 文件先放开
chmod 700 /tmp/permtest       # 但目录关门
su - tester -c 'cat /tmp/permtest/secret.txt'     # 还是 denied，门禁在目录
chmod 755 /tmp/permtest       # 恢复
任务 3：sudo 与用户（20 分钟）
bash
su - tester           # 完整切换身份（要对方密码），exit 退回
sudo cat /etc/shadow  # 以 root 身份执行单条命令（用自己的密码）
su = 变成另一个人；sudo = 借 root 的手做一件事——网工类比：sudo 就像 H3C 的 super 提权 / Cisco 的 enable，而权限位就是文件级的 AAA
你安装系统时勾了"设为管理员"，本质是把你加进了 wheel 组（id 能看到），wheel 组成员才有 sudo 资格
/etc/shadow 存密码哈希，只有 root 能看——体会"为什么系统文件默认权限那么严"
实验收尾清理：exit（如果 su 进去了）、sudo userdel -r tester（删掉测试账号）。

2.验收
(1)drwxr-xr-x 拆成四段，各是什么意思？
答：d代表文件类型d是目录，rwx代表属主权限rwx是读写编辑权限，-xr是同组Group权限xr代表读和执行权限，-x是其他人Other权限x是执行，这个文件的数字权限是755
(2)私钥文件为什么是 600 而不是 644？
答：600是-rw-------:只有属主可读可写，组，其他人完全无权限。644是-rw-r--r--:其他用户拥有读权限
SSH 私钥（id_rsa）属于敏感凭证。
SSH 安全机制：如果私钥对组 / 其他用户开放读权限，ssh 客户端直接拒绝使用该私钥，会报权限过宽错误。
644 情况下，服务器上其他普通用户可以拷贝你的私钥文件，拿去别处登录；泄露风险极高。
私钥标准权限：**600**；对应公钥 `id_rsa.pub` 可以 644。

(3)目录的 x 权限管什么？光有 r 能不能 cd 进去？
答：目录权限含义(重点，目录和文件x意义完全不一样)
(3.1).目录r:可以列出目录文件名(ls)但不能访问文件元数据,不能进入目录
(3.2).目录w:可以在目录内创建、删除、重命名文件(和文件本身权限无关！)
(3.3).目录x:可以进入(cd)该目录,访问目录里面文件的inode,是访问目录内部内容的通行证。
总结:只有r、没有x:可以看到文件名，但是无法cd进去，无法cat目录下任何文件
举例：目录权限 `dr‑r‑‑‑‑‑‑‑ (400)`
ls /test` 能看到里面有哪些文件名
cd /test` → Permission denied
cat /test/a.txt` → 访问失败 
目录常规建议：755 (rwxr‑xr‑x)，必须带 x 权限。

(4)排查"昨晚谁在尝试登录服务器"该看哪个文件、用什么命令？
答：传统 syslog：`/var/log/secure` 登录相关全部在这里（ssh、su、sudo 登录失败 / 成功都记录）
/var/log/messages` 存系统通用信息，不记录 ssh 登录日志，不要搞错。

cat /var/log/secure 				# 查看全部登录记录
grep sshd /var/log/secure 			# 过滤ssh登录，看失败尝试
grep -E "Accepted|Failed" /var/log/secure 	# 看昨晚时间段，过滤Accepted(登录成功) Failed(登录失败)
journalctl -u sshd --since "yesterday 20:00" --until "today 08:00"	 # journald方式(RHEL8+)

Debian/Ubuntu 对应日志文件：`/var/log/auth.log`

关键字：
Accepted publickey/password`：登录成功
Failed password`：密码尝试失败暴力破解
Invalid user`：试探不存在的用户名

(5)su 和 sudo 的区别？为什么生产环境更推荐 sudo？（提示：审计、不用共享 root 密码）
答：su -:切换身份,需要输入目标用户密码,su - 带环境变量，su不带。 sudo:执行单条命令以 root（或其他用户）身份，输入自己当前用户密码，不是 root 密码，受 sudoers 配置控制。
表格

| 维度 | su | sudo |
| --- | --- | --- |
| 密码 | 需要 root 密码 | 使用自己账号密码 |
| 权限 | 一次性完整 root 环境 | 权限细粒度，可以只允许部分命令 |
| 审计日志 | 很难区分是谁用 root 操作，日志只显示 root | `/var/log/secure`记录哪个普通用户执行了 sudo 命令，完整审计 |
| 密码分发 | 多人运维必须共享 root 密码，风险大 | root 密码可以封存不用，不用共享超级用户密码 |

### 生产推荐 sudo 理由（对应提示：审计、不共享 root 密码）
1. **不需要共享 root 密码**：运维人员使用自己账号密码提权，root 密码可以极少使用，降低泄露风险。
2. **审计追溯**：sudo 操作全部记日志，可以查到**哪个运维账号执行了哪条高危命令**；su 切换 root 之后，所有操作日志只显示 root，分不清是谁操作。
3. **权限粒度可控**：`/etc/sudoers`可以限制用户只能执行特定命令，不是完整无限制 root；su 拿到 root 之后权限完全不受控。
4. 风险隔离：错误操作破坏范围可控；不建议日常直接 su‑root 干活。
最佳实践：日常全部 sudo 执行，尽量避免`su - root`。

### 快速记忆小结
1. 权限四段：类型｜属主｜属组｜其他；
2. 私钥 600：防止其他用户读取私钥，ssh 强制校验；
3. 目录 x=cd 进入权限；仅有 r 不能 cd；
4. 登录审计 RHEL 看`/var/log/secure`；过滤 sshd；
5. su 拿 root 要 root 密码；sudo 用自己密码，可审计、不共享 root 密码，生产优选。

