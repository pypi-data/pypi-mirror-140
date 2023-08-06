import urllib.request

import requests
from fake_useragent import UserAgent
from lxml import etree


def load_html(url, timeout=3):
    headers = {'User-Agent': UserAgent().random}
    req = urllib.request.Request(url, headers=headers)
    html = str(urllib.request.urlopen(req, timeout=timeout).read(), 'utf-8')
    return etree.HTML(html)


def ajax(cookie=None, proxies=None):
    headers = {'User-Agent': UserAgent().random}

    if cookie:
        headers['cookie'] = cookie

    if proxies:
        proxies = {
            'http': 'http://' + proxies,
            'https': 'https://' + proxies,
        }

    return headers, proxies


def get(url, timeout=3, params=None, cookie=None, proxies=None):
    headers, proxies = ajax(cookie, proxies)
    return requests.get(url, params=params, headers=headers, proxies=proxies, timeout=timeout)


def post(url, timeout=3, data=None, cookie=None, proxies=None):
    headers, proxies = ajax(cookie, proxies)
    return requests.post(url, data=data, headers=headers, proxies=proxies, timeout=timeout)
