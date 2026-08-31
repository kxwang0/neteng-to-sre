1.今日学习内容
今天的重头戏。Rocky 9 自带 Python 3.9 太旧，我们要从源码编译 3.12——这不只是装软件，更是你第一次完整体验"编译安装"这个 Linux 核心技能，以后装 Nginx、Redis 等源码软件全是这个套路。
版本选型原则：用 3.12（生态兼容最好）；别用已停止维护的 3.8（EOL 不再收安全更新），也别盲目追最新版（部分库的预编译包还没跟上，容易踩依赖坑）。
任务 0：GitHub 自测 + 热身（5 分钟）
bash
gtest
python3 --version          # 看看系统自带的是 3.9.x
which python3              # 住在 /usr/bin/python3（系统的地盘）

任务 1：装编译依赖（15 分钟，今天最重要的一步）
bash
# 先启用 CRB 仓库（Rocky 9 很多 -devel 开发包在里面，默认关闭；一次启用永久有效）
sudo dnf config-manager --set-enabled crb

sudo dnf groupinstall "Development Tools" -y     # gcc、make 等编译全家桶
sudo dnf install -y openssl-devel bzip2-devel libffi-devel zlib-devel \
    readline-devel sqlite-devel xz-devel tk-devel gdbm-devel ncurses-devel

第一坑（返工率最高）：必须在 configure 之前装好这些 -devel 包，尤其 openssl-devel。否则编译出的 Python 缺 ssl 模块，pip 无法走 HTTPS（报 ssl module is not available），只能装好依赖后从头重编。预防永远比返工快。

任务 2：下载源码包（10 分钟）
直接用国内镜像站下载，比 python.org 快得多：
bash
cd /usr/local/src
# 华为云镜像，版本号以镜像站里 3.12 的最新小版本为准（如 3.12.11）
sudo wget https://mirrors.huaweicloud.com/python/3.12.11/Python-3.12.11.tgz
ls -lh Python-3.12.*.tgz        # 确认下载完整（约 25MB）
如果镜像站目录里小版本更新了，浏览器打开 https://mirrors.huaweicloud.com/python/ 看一眼最新的 3.12.x 是几号，替换命令里的版本号即可。

任务 3：解压 + configure（5 分钟）
bash
sudo tar xf Python-3.12.11.tgz && cd Python-3.12.11
sudo ./configure --prefix=/usr/local/python3.12 --enable-optimizations
两个参数的含义（要能理解，验收要考）：
--prefix=/usr/local/python3.12：装到独立目录，和系统 Python 隔离开，井水不犯河水
--enable-optimizations：编译时做性能优化（代价是编译更久，等就完了）
configure 跑完会输出一大段检查报告，最后看到 creating Makefile 没有 ERROR 即可。

任务 4：编译 + 安装（15–25 分钟，等待时间正好写笔记）
bash
sudo make -j$(nproc)        # -j 后面是并行编译的核数，$(nproc) 自动取你的 vCPU 数
sudo make altinstall        # ⚠️ 第二坑：必须 altinstall，不能用 make install
⚠️ 为什么是 altinstall：make install 会把系统的 python3 软链顶掉，而 dnf、系统工具都依赖自带 Python——顶掉后系统工具可能直接罢工。altinstall 只装 python3.12 这个带版本号的命令，不动系统的。
make 等待期间别干等：打开 Cursor 开始写今天的 notes/day06.md（模板在最后），或者复习 Day 1–5 的命令。

任务 5：验证（10 分钟，不过关 = 白编译）
bash
# ① 版本对
/usr/local/python3.12/bin/python3.12 --version

# ② ssl 在（最重要！这步不过 = 回去检查任务 1 的依赖，重装后重新 configure + make）
/usr/local/python3.12/bin/python3.12 -c "import ssl; print(ssl.OPENSSL_VERSION)"

# ③ 做软链，以后敲 python3.12 / pip3.12 就能用
sudo ln -sf /usr/local/python3.12/bin/python3.12 /usr/local/bin/python3.12
sudo ln -sf /usr/local/python3.12/bin/pip3.12 /usr/local/bin/pip3.12

# ④ 冒烟测试：用国内源装个小库，全链路（ssl+pip+网络）验证
pip3.12 install -i https://pypi.tuna.tsinghua.edu.cn/simple requests
python3.12 -c "import requests; print('requests OK')"

2.验证
(1)为什么必须先装 openssl-devel 再 configure？不装会怎样？
答:不先安装openssl-devel会导致编译出的Python缺少ssl模块，pip无法走HTTPS(报ssl module is not available)，只能装好依赖后从头重编

(2)为什么用 make altinstall 而不是 make install？
答:make install会把系统的python3软链顶掉,而dnf,系统工具都依赖自带的Python--顶掉后系统工具可能直接罢工。altinstall只装python3.12这个带版本号的命令。altinstall只装python3.12这个带版本号的命令，不动系统的

(3)--prefix=/usr/local/python3.12 这个参数起了什么作用？
答:安装到独立目录，和系统Python隔离开，井水不犯河水

(4)编译完成后，验证 ssl 模块正常的命令是什么？
答:/usr/local/python3.12/bin/python3.12 -c "import ssl; print(ssl.OPENSSL_VERSION)"

(5)系统的 python3（3.9）和你装的 python3.12 是什么关系？为什么老版本不能卸？
答:两者是共存、互不干扰的两个Python，系统3.9住在/usr/bin/python3，是Rocky的原厂配置，新安装的3.12住在/usr/local/python3.12/，通过软链/usr/local/bin/python3.12使用，敲python3调用的是3.9，敲python3.12才调用3.12命名就分开了
为什么 3.9 不能卸：因为 dnf、系统管理脚本等自带工具就是跑在 3.9 上的，它们 import 的库、依赖的解释器全是自带那套。卸了 3.9 = 把 dnf 的地基抽了，包管理直接瘫痪，系统维护能力归零。
这正是今天所有设计的原因闭环：正因为系统 Python 动不得，才要 --prefix 隔离 + altinstall 共存——以后你在生产服务器上也会无数次用到这个原则：系统的东西别动，自己的东西装到独立目录。







