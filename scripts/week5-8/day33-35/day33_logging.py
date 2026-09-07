import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("backup.log", encoding="utf-8"),   # 落盘
        logging.StreamHandler(),                                # 同时打屏
    ],
)

logging.info("开始采集设备 %s", "192.168.30.252")
logging.warning("设备响应缓慢")
logging.error("设备连接失败")

#五个级别背下来：DEBUG → INFO → WARNING → ERROR → CRITICAL。level=INFO 表示 INFO 及以上的才输出——排障时改成 DEBUG 就能看更细的日志，不用加一行代码。