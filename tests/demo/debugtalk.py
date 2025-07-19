import os
import hashlib
import hmac
from apimeter.logger import log_debug

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

def validate_token(token):
    log_debug(f"validate_token: {token}")
    return len(token) == 16

def validate_token_v2(content):
    log_debug(f"validate_token_v2: {content}")
    raise Exception("test...")
    return len(content["token"]) == 16

def validate_token_v3(content):
    log_debug(f"validate_token_v3: {content}")
    raise Exception("test...")
    return len(content["token"]) == 16

def get_str():
    return "123"

def get_int():
    return 123

def get_float():
    return 123.456

def get_bool():
    return True

def get_none():
    return None

def get_empty_str():
    return ""

def get_empty_list():
    return []

def get_empty_dict():
    return {}

def get_list():
    return [1, 2, 3]

def get_dict():
    return {"a": 1, "b": 2, "c": 3}




"""
script 校验功能演示的自定义函数
"""

def validate_json_structure(json_data):
    """
    验证JSON数据结构
    
    Args:
        json_data: JSON响应数据
        
    Returns:
        bool: 验证结果
    """
    if not isinstance(json_data, dict):
        return False
    
    # 检查必要字段
    required_fields = ["slideshow"]
    for field in required_fields:
        if field not in json_data:
            return False
    
    return True

def check_response_time(elapsed):
    """
    检查响应时间
    
    Args:
        elapsed: 响应时间
        
    Returns:
        bool: 是否在可接受范围内
    """
    # 检查响应时间是否小于2秒
    return elapsed < 2.0

def validate_field_exists(data, field_name):
    """
    验证字段是否存在
    
    Args:
        data: 数据对象
        field_name: 字段名
        
    Returns:
        bool: 字段是否存在
    """
    if isinstance(data, dict):
        return field_name in data
    return False

def count_json_fields(json_data):
    """
    计算JSON对象的字段数量
    
    Args:
        json_data: JSON数据
        
    Returns:
        int: 字段数量
    """
    if isinstance(json_data, dict):
        return len(json_data)
    return 0

def failing_validation_function():
    """
    故意失败的校验函数，用于演示异常处理
    
    Raises:
        Exception: 故意抛出的异常
    """
    raise Exception("raise exception test...")

def validate_email_format(email):
    """
    验证邮箱格式
    
    Args:
        email: 邮箱地址
        
    Returns:
        bool: 格式是否正确
    """
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_user_data(user_data):
    """
    验证用户数据完整性
    
    Args:
        user_data: 用户数据字典
        
    Returns:
        bool: 数据是否完整
        
    Raises:
        AssertionError: 数据不完整时抛出详细错误
    """
    required_fields = ["id", "name", "email"]
    
    for field in required_fields:
        assert field in user_data, f"Missing required field: {field}"
        assert user_data[field] is not None, f"Field '{field}' cannot be None"
    
    # 验证邮箱格式
    assert validate_email_format(user_data["email"]), f"Invalid email format: {user_data['email']}"
    
    # 验证用户ID
    assert isinstance(user_data["id"], int), f"User ID must be integer, got {type(user_data['id'])}"
    assert user_data["id"] > 0, f"User ID must be positive, got {user_data['id']}"
    
    return True