# @Time    : 2022/2/22 9:35
# @Author  : kang.yang@qizhidao.com
# @File    : request.py
import requests
import json as json_util
from qrunner.utils.config import conf
from qrunner.utils.log import logger



IMG = ["jpg", "jpeg", "gif", "bmp", "webp"]


def request(func):
    def wrapper(*args, **kwargs):
        func_name = func.__name__
        print("\n")
        logger.info('-------------- Request -----------------[🚀]')
        try:
            url = list(args)[1]
        except IndexError:
            url = kwargs.get("url", "")
        base_url = conf.get_name('api', 'base_url')
        if (base_url is not None) and ("http" not in url):
            url = base_url + list(args)[1]

        img_file = False
        file_type = url.split(".")[-1]
        if file_type in IMG:
            img_file = True

        logger.debug("[method]: {m}      [url]: {u} \n".format(m=func_name.upper(), u=url))
        auth = kwargs.get("auth", "")
        headers = kwargs.pop("headers", {})
        conf_headers = conf.get_name('api', 'headers')
        if conf_headers != 'None':
            headers.update(json_util.loads(conf_headers))
        kwargs['headers'] = headers
        cookies = kwargs.get("cookies", "")
        params = kwargs.get("params", "")
        data = kwargs.get("data", "")
        json = kwargs.get("json", "")
        if auth != "":
            logger.debug(f"[auth]:\n {auth} \n")
        if headers != "":
            # logger.debug(type(headers))
            logger.debug(f"[headers]:\n {headers} \n")
        if cookies != "":
            logger.debug(f"[cookies]:\n {cookies} \n")
        if params != "":
            logger.debug(f"[params]:\n {params} \n")
        if data != "":
            logger.debug(f"[data]:\n {data} \n")
        if json != "":
            logger.debug(f"[json]:\n {json} \n")

        # running function
        r = func(*args, **kwargs)

        ResponseResult.status_code = r.status_code
        logger.info("-------------- Response ----------------")
        try:
            resp = r.json()
            logger.debug(f"[type]: json \n")
            logger.debug(f"[response]:\n {resp} \n")
            ResponseResult.response = resp
        except BaseException as msg:
            logger.debug("[warning]: {} \n".format(msg))
            if img_file is True:
                logger.debug("[type]: {}".format(file_type))
                ResponseResult.response = r.content
            else:
                logger.debug("[type]: text \n")
                logger.debug(f"[response]:\n {r.text} \n")
                ResponseResult.response = r.text

    return wrapper


class ResponseResult:
    status_code = 200
    response = None


class HttpRequest(object):

    @request
    def get(self, url, params=None, **kwargs):
        base_url = conf.get_name('api', 'base_url')
        if (base_url is not None) and ("http" not in url):
            url = base_url + url
        return requests.get(url, params=params, **kwargs)

    @request
    def post(self, url, data=None, json=None, **kwargs):
        base_url = conf.get_name('api', 'base_url')
        if (base_url is not None) and ("http" not in url):
            url = base_url + url
        return requests.post(url, data=data, json=json, **kwargs)

    @request
    def put(self, url, data=None, **kwargs):
        base_url = conf.get_name('api', 'base_url')
        if (base_url is not None) and ("http" not in url):
            url = base_url + url
        return requests.put(url, data=data, **kwargs)

    @request
    def delete(self, url, **kwargs):
        base_url = conf.get_name('api', 'base_url')
        if (base_url is not None) and ("http" not in url):
            url = base_url + url
        return requests.delete(url, **kwargs)

    @property
    def response(self):
        """
        Returns the result of the response
        :return: response
        """
        return ResponseResult.response

    @property
    def session(self):
        """
        A Requests session.
        """
        s = requests.Session()
        return s

    @staticmethod
    def request(method=None, url=None, headers=None, files=None, data=None,
                params=None, auth=None, cookies=None, hooks=None, json=None):
        """
        A user-created :class:`Request <Request>` object.
        """
        req = requests.Request(method, url, headers, files, data,
                               params, auth, cookies, hooks, json)
        return req
