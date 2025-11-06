# encoding: utf-8

import time
import os
import requests
import urllib3
from requests import Request, Response
from requests.adapters import HTTPAdapter
from requests.exceptions import (
    InvalidSchema,
    InvalidURL,
    MissingSchema,
    RequestException,
)
from urllib3.util.retry import Retry

from apimeter import logger, response
from apimeter.utils import lower_dict_keys, omit_long_data

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# Modified by Devin Zhang, 2025-11-05
# This file is part of a project based on httprunner/httprunner.py,
# licensed under the Apache License 2.0.

def get_req_resp_record(resp_obj):
    """get request and response info from Response() object."""

    def log_print(req_resp_dict, r_type):
        msg = "\n================== {} details ==================\n".format(r_type)
        for key, value in req_resp_dict[r_type].items():
            msg += "{:<16} : {}\n".format(key, repr(value))
        logger.log_debug(msg)

    req_resp_dict = {"request": {}, "response": {}}

    # record actual request info
    req_resp_dict["request"]["url"] = resp_obj.request.url
    req_resp_dict["request"]["method"] = resp_obj.request.method
    req_resp_dict["request"]["headers"] = dict(resp_obj.request.headers)

    request_body = resp_obj.request.body
    if request_body:
        request_content_type = lower_dict_keys(req_resp_dict["request"]["headers"]).get(
            "content-type"
        )
        if request_content_type and "multipart/form-data" in request_content_type:
            # upload file type
            req_resp_dict["request"]["body"] = "upload file stream (OMITTED)"
        else:
            req_resp_dict["request"]["body"] = request_body

    # log request details in debug mode
    log_print(req_resp_dict, "request")

    # record response info
    req_resp_dict["response"]["ok"] = resp_obj.ok
    req_resp_dict["response"]["url"] = resp_obj.url
    req_resp_dict["response"]["status_code"] = resp_obj.status_code
    req_resp_dict["response"]["reason"] = resp_obj.reason
    req_resp_dict["response"]["cookies"] = resp_obj.cookies or {}
    req_resp_dict["response"]["encoding"] = resp_obj.encoding
    resp_headers = dict(resp_obj.headers)
    req_resp_dict["response"]["headers"] = resp_headers

    lower_resp_headers = lower_dict_keys(resp_headers)
    content_type = lower_resp_headers.get("content-type", "")
    req_resp_dict["response"]["content_type"] = content_type

    if "image" in content_type:
        # response is image type, record bytes content only
        req_resp_dict["response"]["body"] = resp_obj.content
    else:
        try:
            # try to record json data
            if isinstance(resp_obj, response.ResponseObject):
                req_resp_dict["response"]["body"] = resp_obj.json
            else:
                req_resp_dict["response"]["body"] = resp_obj.json()
        except ValueError:
            # only record at most 512 text charactors
            resp_text = resp_obj.text
            req_resp_dict["response"]["body"] = omit_long_data(resp_text)

    # log response details in debug mode
    log_print(req_resp_dict, "response")

    return req_resp_dict


class ApiResponse(Response):
    def raise_for_status(self):
        if hasattr(self, "error") and self.error:
            raise self.error
        Response.raise_for_status(self)


class HttpSession(requests.Session):
    """
    Class for performing HTTP requests and holding (session-) cookies between requests (in order
    to be able to log in and out of websites). Each request is logged so that HttpRunner can
    display statistics.

    This is a slightly extended version of `python-request <http://python-requests.org>`_'s
    :py:class:`requests.Session` class and mostly this class works exactly the same.
    """

    def __init__(self):
        super(HttpSession, self).__init__()
        self.init_meta_data()

        # 配置重试策略，解决连接池中僵尸连接导致的 Connection reset 问题
        # 当 SSL 握手失败或连接被重置时，自动重试而不是直接失败
        retry_strategy = Retry(
            total=3,              # 总共重试3次
            connect=3,            # 连接失败（包括SSL握手失败）重试3次
            read=2,               # 读取超时重试2次
            status_forcelist=[500, 502, 503, 504],  # 这些HTTP状态码也重试
            allowed_methods=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE", "POST"],
            backoff_factor=0.5,   # 重试延迟：0.5s, 1s, 2s
            raise_on_status=False,
        )

        # 是否禁用连接池（通过环境变量控制）
        # 禁用连接池可以避免复用僵尸连接，但会略微降低性能
        disable_pool = os.getenv("APIMETER_DISABLE_POOL", "false").lower() in ("true", "on", "yes", "1")
        pool_size = 1 if disable_pool else 20

        # 配置 HTTP 适配器，保留连接池以提升性能，但配置重试机制以提升稳定性
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=pool_size,   # 连接池大小
            pool_maxsize=pool_size,       # 最大连接数
            pool_block=False,             # 连接池满时不阻塞
        )

        # 为 http 和 https 协议挂载适配器
        self.mount('http://', adapter)
        self.mount('https://', adapter)

    def init_meta_data(self):
        """initialize meta_data, it will store detail data of request and response"""
        self.meta_data = {
            "name": "",
            "data": [
                {
                    "request": {"url": "N/A", "method": "N/A", "headers": {}},
                    "response": {
                        "status_code": "N/A",
                        "headers": {},
                        "encoding": None,
                        "content_type": "",
                    },
                }
            ],
            "stat": {
                "content_size": "N/A",
                "response_time_ms": "N/A",
                "elapsed_ms": "N/A",
            },
        }

    def update_last_req_resp_record(self, resp_obj):
        """
        update request and response info from Response() object.
        """
        self.meta_data["data"].pop()
        self.meta_data["data"].append(get_req_resp_record(resp_obj))

    def request(self, method, url, name=None, **kwargs):
        """
        Constructs and sends a :py:class:`requests.Request`.
        Returns :py:class:`requests.Response` object.

        :param method:
            method for the new :class:`Request` object.
        :param url:
            URL for the new :class:`Request` object.
        :param name: (optional)
            Placeholder, make compatible with Locust's HttpSession
        :param params: (optional)
            Dictionary or bytes to be sent in the query string for the :class:`Request`.
        :param data: (optional)
            Dictionary or bytes to send in the body of the :class:`Request`.
        :param headers: (optional)
            Dictionary of HTTP Headers to send with the :class:`Request`.
        :param cookies: (optional)
            Dict or CookieJar object to send with the :class:`Request`.
        :param files: (optional)
            Dictionary of ``'filename': file-like-objects`` for multipart encoding upload.
        :param auth: (optional)
            Auth tuple or callable to enable Basic/Digest/Custom HTTP Auth.
        :param timeout: (optional)
            How long to wait for the server to send data before giving up, as a float, or \
            a (`connect timeout, read timeout <user/advanced.html#timeouts>`_) tuple.
            :type timeout: float or tuple
        :param allow_redirects: (optional)
            Set to True by default.
        :type allow_redirects: bool
        :param proxies: (optional)
            Dictionary mapping protocol to the URL of the proxy.
        :param stream: (optional)
            whether to immediately download the response content. Defaults to ``False``.
        :param verify: (optional)
            if ``True``, the SSL cert will be verified. A CA_BUNDLE path can also be provided.
        :param cert: (optional)
            if String, path to ssl client cert file (.pem). If Tuple, ('cert', 'key') pair.
        """
        self.init_meta_data()

        # record test name
        self.meta_data["name"] = name

        # record original request info
        self.meta_data["data"][0]["request"]["method"] = method
        self.meta_data["data"][0]["request"]["url"] = url
        # 设置超时时间
        default_timeout = int(os.getenv("APIMETER_DEFAULT_TIMEOUT", "120"))
        kwargs.setdefault("timeout", default_timeout)
        # 设置 Connection 方式
        close_connection = os.getenv("APIMETER_CLOSE_CONNECTION", "false").lower() in ("true", "on", "yes", "1")
        if close_connection:
            headers = kwargs.get("headers", {})
            if headers is None:
                headers = {}
            # 使用不区分大小写的检查，避免重复设置
            headers_lower = {k.lower(): k for k in headers.keys()}
            if "connection" not in headers_lower:
                headers["Connection"] = "close"
            kwargs["headers"] = headers

        self.meta_data["data"][0]["request"].update(kwargs)

        start_timestamp = time.time()
        response = self._send_request_safe_mode(method, url, **kwargs)
        response_time_ms = round((time.time() - start_timestamp) * 1000, 2)

        # get the length of the content, but if the argument stream is set to True, we take
        # the size from the content-length header, in order to not trigger fetching of the body
        if kwargs.get("stream", False):
            content_size = int(dict(response.headers).get("content-length") or 0)
        else:
            content_size = len(response.content or "")

        # record the consumed time
        self.meta_data["stat"] = {
            "response_time_ms": response_time_ms,
            "elapsed_ms": response.elapsed.microseconds / 1000.0,
            "content_size": content_size,
        }

        # record request and response histories, include 30X redirection
        response_list = response.history + [response]
        self.meta_data["data"] = [
            get_req_resp_record(resp_obj) for resp_obj in response_list
        ]

        try:
            response.raise_for_status()
        except RequestException as e:
            logger.log_error("{exception}".format(exception=str(e)))
        else:
            logger.log_info(
                """status_code: {}, response_time(ms): {} ms, response_length: {} bytes\n""".format(
                    response.status_code, response_time_ms, content_size
                )
            )

        return response

    def _send_request_safe_mode(self, method, url, **kwargs):
        """
        Send a HTTP request, and catch any exception that might occur due to connection problems.
        Safe mode has been removed from requests 1.x.
        """
        try:
            msg = "processed request:\n"
            msg += "> {method} {url}\n".format(method=method, url=url)
            msg += "> kwargs: {kwargs}".format(kwargs=kwargs)
            logger.log_debug(msg)
            return requests.Session.request(self, method, url, **kwargs)
        except (MissingSchema, InvalidSchema, InvalidURL):
            raise
        except RequestException as ex:
            resp = ApiResponse()
            resp.error = ex
            resp.status_code = 0  # with this status_code, content returns None
            resp.request = Request(method, url).prepare()
            return resp
