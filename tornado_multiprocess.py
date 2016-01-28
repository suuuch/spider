#!/usr/bin/env python
# -*- coding:utf-8 -*-

import time
from multiprocessing import Pool
from datetime import timedelta
from tornado import httpclient, gen, ioloop, queues


class AsySpider(object):
    """A simple class of asynchronous spider."""
    def __init__(self, urls, concurrency):
        urls.reverse()
        self.urls = urls
        self.concurrency = concurrency
        self._q = queues.Queue()
        self._fetching = set()
        self._fetched = set()

    def handle_page(self, url, html):
        filename = url.rsplit('/', 1)[1]
        with open(filename, 'w+') as f:
            f.write(html)

    def fetch(self,url,**kwargs):
        fetch = getattr(httpclient.AsyncHTTPClient(), 'fetch')
        return fetch(url, **kwargs)

    @gen.coroutine
    def get_page(self, url):
        try:
            response = yield self.fetch(url)
            print('######fetched %s' % url)
        except Exception as e:
            print('Exception: %s %s' % (e, url))
            raise gen.Return('')
        raise gen.Return(response.body)

    @gen.coroutine
    def _run(self):

        @gen.coroutine
        def fetch_url():
            current_url = yield self._q.get()
            try:
                if current_url in self._fetching:
                    return

                print('fetching****** %s' % current_url)
                self._fetching.add(current_url)
                html = yield self.get_page(current_url)
                self._fetched.add(current_url)

                self.handle_page(current_url, html)

                for i in range(self.concurrency):
                    if self.urls:
                        yield self._q.put(self.urls.pop())

            finally:
                self._q.task_done()

        @gen.coroutine
        def worker():
            while True:
                yield fetch_url()

        self._q.put(self.urls.pop())

        # Start workers, then wait for the work queue to be empty.
        for _ in range(self.concurrency):
            worker()
        yield self._q.join(timeout=timedelta(seconds=300000))
        assert self._fetching == self._fetched

    def run(self):
        io_loop = ioloop.IOLoop.current()
        io_loop.run_sync(self._run)


class MySpider(AsySpider):

    def fetch(self, url, **kwargs):
        """重写父类fetch方法可以添加cookies，headers，timeout等信息"""
        # 从浏览器拷贝cookie字符串
        cookies_str = ""
        headers = {
            'User-Agent': 'mozilla/5.0 (compatible; baiduspider/2.0; +http://www.baidu.com/search/spider.html)',
            'cookie': cookies_str
        }
        return super(MySpider, self).fetch(   # 参数参考tornado文档
            url, headers=headers, request_timeout=1
        )


def run_spider(beg, end):
    urls = []
    for page in range(beg, end):
        urls.append('http://127.0.0.1/%s.htm' % page)
    s = MySpider(urls, 10)
    s.run()

def main():
    _st = time.time()
    p = Pool()
    all_num = 73000
    num = 4    # number of cpu cores
    per_num, left = divmod(all_num, num)
    s = range(0, all_num, per_num)
    res = []
    for i in range(len(s)-1):
        res.append((s[i], s[i+1]))
    res.append((s[len(s)-1], all_num))
    print res

    for i in res:
        p.apply_async(run_spider, args=(i[0], i[1],))
    p.close()
    p.join()

    print time.time()-_st


if __name__ == '__main__':
    main()
