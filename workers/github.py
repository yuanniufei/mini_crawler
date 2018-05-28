# -*- coding: utf-8 -*-
import asyncio
import logging
import os
import random
import signal
import sys
import time

import aiohttp
import aioredis
import uvloop

from crawlers.github.constants import redis_github_stars_list_key
from crawlers.github.fetchers import GithubStarsFetcher
from crawlers.github.handlers import GithubProfileHandler


async def create_global_session(loop):
    # TODO TCP 需要限制一下连接池大小，不知道为什么协程锁搞不定。
    session = aiohttp.ClientSession(loop=loop, connector=aiohttp.TCPConnector(verify_ssl=False, loop=loop))
    return session


async def close_session(session):
    await session.close()


async def close_redis_pool(pool):
    return pool.close()


# TODO 要拆分到 Dispatcher 里。
async def consumer(http_session, redis_pool, max_concurrent_sem):
    # profile_fetcher = GithubProfileFetcher(http_session)
    stars_fetcher = GithubStarsFetcher(http_session)
    while True:
        async with max_concurrent_sem:
            with await redis_pool as redis_client:
                state = await stars_fetcher.before(redis_client, redis_github_stars_list_key)
                if not state:
                    break

                # result = await profile_fetcher.fetch()
                result = await stars_fetcher.fetch()
                print(result)

                handler = GithubProfileHandler(redis_client)
                await handler.handle(result)
                await asyncio.sleep(random.randint(1, 2))


def main(crawler_conf, redis_conf, mysql_conf, execute_dir):
    # 注：要想开启 asyncio 的日志，必须 import 的顺序是 asyncio 在前。
    log_dir_path = os.path.join(execute_dir, 'log')
    if not os.path.exists(log_dir_path):
        os.makedirs(log_dir_path)

    log_file_path = os.path.join(execute_dir, 'log', 'github.log')
    log_handler = logging.FileHandler(log_file_path)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    log_handler.setFormatter(formatter)

    logger = logging.getLogger('asyncio')
    logger.setLevel(logging.INFO)
    logger.addHandler(log_handler)

    # 初始化事件循环
    loop = uvloop.new_event_loop()
    asyncio.set_event_loop(loop)

    max_concurrent_sem = asyncio.Semaphore(value=crawler_conf['consumer_sem'], loop=loop)

    # 初始化全局 aiohttp.ClientSession 和 redis pool
    initialize_tasks = list()
    initialize_tasks.append(create_global_session(loop))
    initialize_tasks.append(aioredis.create_pool(
        (redis_conf['host'], redis_conf['port']), db=redis_conf['db'],
        minsize=redis_conf['pool_minsize'], maxsize=redis_conf['pool_maxsize'], loop=loop
    ))

    results = loop.run_until_complete(asyncio.gather(*initialize_tasks))
    aiohttp_session = results[0]
    redis_pool = results[1]

    tasks = list()
    for _ in range(crawler_conf['consumer_num']):
        tasks.append(consumer(aiohttp_session, redis_pool, max_concurrent_sem))

    # 收到 kill 信号之后，主程序可以做 finally 操作。
    def signal_term_handler(sig, frame):
        sys.exit(0)

    # TODO handle kill 信号，将失效的单词放回队列中。
    signal.signal(signal.SIGTERM, signal_term_handler)
    try:
        loop.run_until_complete(asyncio.gather(*tasks))
    except KeyboardInterrupt:
        pass
    finally:
        loop.run_until_complete(asyncio.ensure_future(close_session(aiohttp_session), loop=loop))
        loop.run_until_complete(asyncio.ensure_future(close_redis_pool(redis_pool), loop=loop))

        time.sleep(5)
        loop.close()
