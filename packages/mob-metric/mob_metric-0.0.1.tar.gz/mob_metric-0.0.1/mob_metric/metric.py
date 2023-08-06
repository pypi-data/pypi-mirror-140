# -*- coding: utf-8 -*-
# @Time : 2022/2/16 11:06
# Author: JingHaiQiang
import json
import os
import re
import socket

from redis import StrictRedis
from scrapy import signals
import datetime
from threading import Timer


# scrapy extension 打点记录当前爬虫运行情况

def get_one_min_later(step=1):
    """
     获取下一分钟的整点时间戳 按整点存进去
    :param step:
    :return:
    """
    dt = datetime.datetime.now()
    td = datetime.timedelta(
        days=0,
        seconds=dt.second,
        microseconds=dt.microsecond,
        milliseconds=0,
        minutes=-step,
        hours=0,
        weeks=0
    )
    new_dt = dt - td
    timestamp = int(new_dt.timestamp())  # 对于 python 3 可以直接使用 timestamp 获取时间戳
    return timestamp


def get_localhost_ip():
    """
    利用 UDP 协议来实现的，生成一个UDP包，把自己的 IP 放如到 UDP 协议头中，然后从UDP包中获取本机的IP。
    这个方法并不会真实的向外部发包，所以用抓包工具是看不到的
    :return:
    """
    s = None
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    finally:
        if s:
            s.close()
    return ip


def get_redis_setting(crawler):
    REDIS_URL = crawler.settings.get('REDIS_URL')
    if REDIS_URL:
        c_ = re.compile('redis://(.*?):(.*?)@(.*?):(\d+)')
        c = c_.search(REDIS_URL)
        if c:
            REDIS_PASSWD = c.group(1)
            REDIS_DB = c.group(2)
            REDIS_HOST = c.group(3)
            REDIS_PORT = c.group(4)
            if REDIS_PASSWD and REDIS_DB and REDIS_HOST and REDIS_PORT:
                return REDIS_PASSWD, REDIS_DB, REDIS_HOST, REDIS_PORT
    REDIS_PARAMS = crawler.settings.get('REDIS_PARAMS')
    if REDIS_PARAMS and REDIS_PARAMS.get('password'):
        REDIS_PASSWD = REDIS_PARAMS.get('password')
    else:
        REDIS_PASSWD = crawler.settings.get('REDIS_PASSWD')

    if REDIS_PARAMS and REDIS_PARAMS.get('db'):

        REDIS_DB = REDIS_PARAMS.get('db')
    else:
        REDIS_DB = crawler.settings.get('REDIS_DB', 5)
    REDIS_HOST = crawler.settings.get('REDIS_HOST')
    REDIS_PORT = crawler.settings.get('REDIS_PORT')
    return REDIS_PASSWD, REDIS_DB, REDIS_HOST, REDIS_PORT


class MerticExtension:
    def __init__(self, crawler, REDIS_HOST, REDIS_PORT, REDIS_PASSWD, REDIS_DB, interval):
        self.exit_code = False
        self.interval = interval
        self.crawler = crawler
        self.client = StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, password=REDIS_PASSWD,
                                  decode_responses=True)
        self.stats_keys = set()
        self.cur_d = {
            'log_info': 0,
            'log_warning': 0,
            'requested': 0,
            'request_bytes': 0,
            'response': 0,
            'response_bytes': 0,
            'response_200': 0,
            'response_301': 0,
            'response_404': 0,
            'responsed': 0,
            'item': 0,
            'filtered': 0,
            'download_err': 0,
            'error_count': 0
        }
        self.pid = os.getpid()

    @classmethod
    def from_crawler(cls, crawler):
        REDIS_PASSWD, REDIS_DB, REDIS_HOST, REDIS_PORT = get_redis_setting(crawler)
        interval = crawler.settings.get('INTERVAL', 60)
        ext = cls(crawler, REDIS_HOST, REDIS_PORT, REDIS_PASSWD, REDIS_DB, interval)
        crawler.signals.connect(ext.engine_started, signal=signals.engine_started)
        crawler.signals.connect(ext.engine_stopped, signal=signals.engine_stopped)
        crawler.signals.connect(ext.spider_closed, signal=signals.spider_closed)
        crawler.signals.connect(ext.spider_opened, signal=signals.spider_opened)
        return ext

    def engine_started(self):
        Timer(self.interval, self.handle_stat).start()

    def engine_stopped(self):
        self.exit_code = True

    def spider_closed(self, spider, reason):
        pass

    def spider_opened(self, spider):
        pass

    def handle_stat(self):
        stats = self.crawler.stats.get_stats()

        d = {
            'log_info': stats.get('log_count/INFO', 0),
            'dequeued': stats.get('scheduler/dequeued/redis', 0),
            'log_warning': stats.get('log_count/WARNING', 0),
            'requested': stats.get('downloader/request_count', 0),
            'request_bytes': stats.get('downloader/request_bytes', 0),
            'response': stats.get('downloader/response_count', 0),
            'response_bytes': stats.get('downloader/response_bytes', 0),
            'response_200': stats.get('downloader/response_status_count/200', 0),
            'response_301': stats.get('downloader/response_status_count/301', 0),
            'response_404': stats.get('downloader/response_status_count/404', 0),
            'responsed': stats.get('response_received_count', 0),
            'item': stats.get('item_scraped_count', 0),
            'depth': stats.get('request_depth_max', 0),
            'filtered': stats.get('bloomfilter/filtered', 0),
            'enqueued': stats.get('scheduler/enqueued/redis', 0),
            'spider_name': self.crawler.spider.name,
            'download_err': stats.get('downloader/exception_count', 0),
            'error_count': stats.get('error_count', 0),
        }
        for key in self.cur_d:
            d[key], self.cur_d[key] = d[key] - self.cur_d[key], d[key]

        redis_d = {
            "identity": get_localhost_ip() + '_' + str(self.pid),
            'name': self.crawler.spider.name,
            'type': 1,
            'state': 1,
            'total_count': stats.get('scheduler/enqueued/redis', 0),
            'left_count': self.client.llen(self.crawler.spider.redis_key),
            'success_count': d['item'],
            'error_count': d['response_301'] + d['response_404'] + d['download_err'] if not d['error_count'] else d[
                'error_count'],
            # 优先中间键打点
            'page_per_second': d['response_200'],
            "timestamp": get_one_min_later(),
        }
        self.client.lpush('metric:' + self.crawler.spider.name, json.dumps(redis_d, ensure_ascii=False))
        self.stats_keys.update(stats.keys())
        if not self.exit_code:
            Timer(self.interval, self.handle_stat).start()
