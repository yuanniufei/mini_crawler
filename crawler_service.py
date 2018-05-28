# -*- coding: utf-8 -*-
# 调度器，负责调度 worker.py，主要是因为两个原因：
#   1. worker.py 的协程不能在一个 loop 里开太多，否则协调会消耗大量时间片；
#   2. 代理池存在运行一段时间后出现大量代理拒绝连接的异常，需要暂时退出、重启。
import os
import sys
import time
import signal
import argparse
import configparser

from multiprocessing import Process

# from workers.github import main as github_worker
from workers.stackoverflow import main as stackoverflow_tags_worker

def main():
    config = configparser.ConfigParser()

    ap = argparse.ArgumentParser(description='crawler_service')
    ap.add_argument('-d', '--execute_dir', type=str, help='crawler_service execute directory', default=os.getcwd())
    args = ap.parse_args()
    os.chdir(args.execute_dir)

    config_file_path = os.path.join(args.execute_dir, 'conf', 'crawler_service.cfg')
    config.read(config_file_path)

    consumer_num = config.get('crawler', 'consumer_num')
    consumer_sem = config.get('crawler', 'consumer_sem')
    crawler_conf = {'consumer_num': int(consumer_num), 'consumer_sem': int(consumer_sem)}

    redis_host = config.get('redis', 'host')
    redis_port = config.get('redis', 'port')
    redis_db = config.get('redis', 'db')
    redis_pool_minsize = config.get('redis', 'pool_minsize')
    redis_pool_maxsize = config.get('redis', 'pool_maxsize')
    redis_conf = {'host': redis_host, 'port': int(redis_port), 'db': int(redis_db),
                  'pool_minsize': int(redis_pool_minsize), 'pool_maxsize': int(redis_pool_maxsize)}

    mysql_host = config.get('mysql', 'host')
    mysql_port = config.get('mysql', 'port')
    mysql_db = config.get('mysql', 'db')
    mysql_user = config.get('mysql', 'user')
    mysql_password = config.get('mysql', 'password')
    mysql_conf = {'host': mysql_host, 'port': int(mysql_port), 'db': mysql_db,
                  'user': mysql_user, 'password': mysql_password}

    exit_flag = False

    # 收到 kill 信号之后，主程序可以做 finally 操作。
    # 有个问题，父进程收到 kill 信号时，能否将该信号传递给子进程？
    def signal_term_handler(sig, frame):
        global exit_flag
        exit_flag = True
        sys.exit(0)

    signal.signal(signal.SIGTERM, signal_term_handler)
    while True:
        if exit_flag:
            break

        try:
            p1 = Process(target=stackoverflow_tags_worker, args=(crawler_conf, redis_conf, mysql_conf, args.execute_dir))
            p1.start()

            p1.join()
        except KeyboardInterrupt:
            exit_flag = True
            pass
        finally:
            # 因为这里是杀掉父进程，子进程会挂靠到根进程上。
            p1.terminate()

            time.sleep(120)


if __name__ == '__main__':
    main()
