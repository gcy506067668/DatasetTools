# -*- coding: utf-8 -*-
import logging
import os

from icrawler.builtin import (BingImageCrawler, BaiduImageCrawler,
                              GoogleImageCrawler)

from crawlers.mcrawler.downloader import ImageDownloader


class Crawler:
    def __init__(self):
        pass

    def findPic(self, keys, path, max_num_every_cw=1000):
        if not os.path.isdir(path):
            os.mkdir(path)

        if isinstance(keys, str):
            self._baidu_cw(keys, path, max_num_every_cw)
            self._bing_cw(keys, path, max_num_every_cw)
            self._google_cw(keys, path, max_num_every_cw)
        elif isinstance(keys, (list, tuple)):
            for item in keys:
                self._baidu_cw(item, path, max_num_every_cw)
                self._bing_cw(item, path, max_num_every_cw)
                self._google_cw(item, path, max_num_every_cw)

        pass

    def _google_cw(self, key, path, max_num):
        path = os.path.join(path, "google")
        if not os.path.isdir(path):
            os.mkdir(path)
        google_crawler = GoogleImageCrawler(
            downloader_threads=4,
            storage={'root_dir': path},
            log_level=logging.INFO)
        google_crawler.crawl(key, max_num=max_num)

    def _bing_cw(self, key, path, max_num):
        path = os.path.join(path, "bing")
        if not os.path.isdir(path):
            os.mkdir(path)
        bing_crawler = BingImageCrawler(
            downloader_cls=ImageDownloader,
            downloader_threads=4,
            storage={'root_dir': path},
            log_level=logging.INFO)
        bing_crawler.crawl(key, max_num=max_num)
        pass

    def _baidu_cw(self, key, path, max_num):
        path = os.path.join(path, "baidu")
        if not os.path.isdir(path):
            os.mkdir(path)
        bing_crawler = BaiduImageCrawler(
            downloader_cls=ImageDownloader,
            downloader_threads=4,
            storage={'root_dir': path},
            log_level=logging.INFO)
        bing_crawler.crawl(key, max_num=max_num)
