import threading


def dead_loop():
    while True:
        pass


# 新起一个死循环线程
t = threading.Thread(target=dead_loop)
t.start()

# 主线程也进入死循环
dead_loop()

t.join()
