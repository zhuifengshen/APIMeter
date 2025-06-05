import os
import hashlib
import hmac

BASE_URL = "http://127.0.0.1:5000"
SECRET_KEY = "DebugTalk"

def get_base_url():
    return BASE_URL

def sum_status_code(status_code, expect_sum):
    """sum status code digits
    e.g. 400 => 4, 201 => 3
    """
    sum_value = 0
    for digit in str(status_code):
        sum_value += int(digit)

    assert sum_value == expect_sum


def is_status_code_200(status_code):
    return status_code == 200


def get_sign(*args):
    content = "".join(args).encode("ascii")
    sign_key = SECRET_KEY.encode("ascii")
    sign = hmac.new(sign_key, content, hashlib.sha1).hexdigest()
    print(f"sign v1: {sign}")
    return sign

def get_sign_v2(args_list):
    content = "".join(args_list).encode("ascii")
    sign_key = SECRET_KEY.encode("ascii")
    sign = hmac.new(sign_key, content, hashlib.sha1).hexdigest()
    print(f"sign v2: {sign}")
    return sign

def get_sign_v3(args_object):
    args_list = [args_object["device_sn"], args_object["os_platform"], args_object["app_version"]]
    content = "".join(args_list).encode("ascii")
    sign_key = SECRET_KEY.encode("ascii")
    sign = hmac.new(sign_key, content, hashlib.sha1).hexdigest()
    print(f"sign v3: {sign}")
    return sign