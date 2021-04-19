import sys
import json
import requests
import traceback
import time
import pymongo
import random
from urllib.request import urlopen
from pkg_resources import parse_version    
from selenium.webdriver.support.wait import WebDriverWait



def wait_web_driver(web_driver, time_out, interval=0.5, xpath=None, css=None):
    """
    浏览器显性等待
    :param web_driver:web_driver
    :param time_out:最长等待时间
    :param interval:检查元素的间隔时间
    :param xpath:xpath选择器
    :param css:css选择器
    """
    interval = interval if interval != 0.5 else 0.5
    if css:
        WebDriverWait(web_driver, time_out, interval).until(lambda x: x.find_element_by_css_selector(css))
    elif xpath:
        WebDriverWait(web_driver, time_out, interval).until(lambda x: x.find_element_by_xpath(xpath))
    else:
        raise ValueError('xpath或css参数不能为空')
class Timer(object):
    """
    计时器，对于需要计时的代码进行with操作：
    with Timer() as timer:
        ...
        ...
    print(timer.cost)
    ...
    """
    def __init__(self, start=None):
        self.start = start if start is not None else time.time()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop = time.time()
        self.cost = self.stop - self.start
        return exc_type is None



"""解析请求头"""
def format_headers(string)->dict:
    """
    将在Chrome上复制下来的浏览器UA格式化成字典，以\n为切割点
    :param string: 使用三引号的字符串
    :return:
    """
    string = string.strip().replace(' ', '').split('\n')
    new_headers = {}
    for key_value in string:
        key_value_list = key_value.split(':')
        if len(key_value_list) > 2:
            new_headers.update({key_value_list[0]: ':'.join(key_value_list[1::])})
        else:
            new_headers.update({key_value_list[0]: key_value_list[1]})
    return new_headers


"""解析URL"""
from urllib.parse import unquote
def format_parameter(request_url):
    """
    格式化url并返回接口链接与格式化后的参数
    :param request_url:请求链接
    :return:接口链接，格式化后的参数
    """
    assert isinstance(request_url, str)
    para_dict = {}
    _ = [para_dict.update({p.split('=')[0]:p.split('=')[1]}) for p in unquote(request_url).split('?')[1].split('&')]
    return request_url.split('?')[0], para_dict

"""请求循环"""
def request(url):
    while True:
        try:
            resp = requests.get(url, headers=headers, timeout=30, verify=False)
        except Exception as error:
            print(url,error)
            time.sleep(20)
            resp = ''
            request(url)
        if resp:
            break
    return resp

# def proxy():
#     resp = requests.get('http://www.feilongip.com/250.txt')
#     resp = resp.text.split()
#     proxies = []
#     for _ in resp:
#         proxies.append({'http': 'http://{}'.format(_), 'https': 'http://{}'.format(_)})
#     return random.sample(proxies, 1)[0]
def proxy():
    with open('proxy.txt', 'r+') as r:
        proxies = r.read()
        proxies = json.loads(proxies.replace("'", '"'))
        proxy = random.sample(proxies['proxies'], 1)[0]
        return proxy

class MongoDbClient:
    """
    mongodb的Client上下文管理器
    with MongoDbClient('collection') as mongo:
        mongo.xxx()
    """
    def __init__(self, collection):
        self.host = '127.0.0.1'
        self.port = 27017
        self.db_name = 'test'
        self.user = 'zane'
        self.pwd = '*#06#'
        self.collection = collection
        self.client = pymongo.MongoClient(
            host=self.host,
            # username=self.user,
            # password=self.pwd,
            port=self.port
        )

    def __enter__(self):
        return self.client[self.db_name][self.collection]

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.close()

def id2time(object_id):
    """mongodb _id转时间"""
    timeStamp = int(object_id[:8], 16)
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timeStamp))

def get_non_developer_driver():
    """
    console输入 window.navigator.webdriver进行检查
    一般的chromedriver会被检测出是模拟浏览器,
    开启实验性功能参数excludeSwitches，则可以绕过此识别
    来源:https://zhuanlan.zhihu.com/p/56546468
    :return:
    """
    option = ChromeOptions()
    option.add_experimental_option('excludeSwitches', ['enable-automation'])
    driver = Chrome(options=option)
    return driver


def versions(pkg_name):
    url = f'https://pypi.python.org/pypi/{pkg_name}/json'
    releases = json.loads(urlopen(url).read())['releases']
    return sorted(releases, key=parse_version, reverse=True)    


if __name__ == '__main__':
    print(versions('torch'))