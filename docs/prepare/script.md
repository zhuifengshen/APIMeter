## 📋 **自定义脚本校验功能概述**

`script` 是 HttpRunner 提供的简洁而强大的校验功能，支持使用 Python 脚本进行灵活的响应校验。它采用 **"异常即失败"** 的设计理念，与 Python assert 语句完全一致，不增加用户记忆负担，符合开发者直觉。

## 🎯 **核心特性**

1. **两种校验模式**
   - **Python 脚本** - 支持任意 Python 语句（assert、条件判断、循环等）
   - **自定义函数** - 调用 debugtalk.py 中定义的校验函数

2. **异常即失败原则**
   - 脚本执行无异常 = 校验通过
   - 脚本抛出异常 = 校验失败
   - 与 Python assert 语句设计理念一致

3. **逐条执行机制**
   - 每条脚本独立执行
   - 单条失败不中断其他脚本继续执行
   - 详细的错误日志和测试报告

4. **丰富的内置功变量**
   - 直接访问响应数据：`status_code`, `headers`, `content`, `json` 等
   - 支持点号访问语法：`content.user.name`
   - 变量引用：`$token`, `$user_id`


## 🚀 **基本语法**

在测试用例中使用 `script` 字段：

```yaml
teststeps:
- name: 示例测试步骤
  request:
    url: /api/example
    method: GET
  script:
    - assert status_code == 200
    - assert content.success is True
    - ${custom_validation_function($token)}
```

## 🔧 **可用变量**

在 `script` 中可以直接使用以下响应变量：

| 变量名 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| `status_code` | int | HTTP状态码 | `assert status_code == 200` |
| `headers` | proxy | 响应头信息 | `assert headers["Content-Type"] == "application/json"` |
| `cookies` | proxy | Cookie信息 | `assert "session_id" in cookies` |
| `content` | proxy | 响应内容（自动解析JSON） | `assert content.token is not None` |
| `body` | proxy | 原始响应体 | `assert "success" in body` |
| `text` | proxy | 响应文本 | `assert len(text) > 0` |
| `json` | proxy | JSON响应内容 | `assert json["code"] == 0` |
| `elapsed` | proxy | 响应时间对象 | `assert elapsed.total_seconds < 2.0` |
| `encoding` | str | 响应编码 | `assert encoding == "utf-8"` |
| `ok` | bool | 请求是否成功 | `assert ok is True` |
| `reason` | str | 状态码说明 | `assert reason == "OK"` |
| `url` | str | 请求URL | `assert "api" in url` |
| `response` | object | 完整响应对象 | `assert response.status_code == 200` |

## 🧪 单元测试 (`tests/test_validator.py`)

- ✅ Assert 语句校验（成功/失败）
- ✅ 自定义函数校验（成功/失败）
- ✅ 异常处理（语法错误、变量不存在等）
- ✅ 响应字段访问（headers、content、json等）
- ✅ 变量引用和解析
- ✅ 复杂表达式和条件校验
- ✅ 异常分类处理（关键异常 vs 运行时异常）
```bash
# 运行所有validator测试
python -m unittest tests.test_validator -v

# 运行特定测试
python -m unittest tests.test_validator.TestValidator.test_validate_script_assert_success -v
```

## 🔧 核心组件技术实现

1. **Validator.validate_script()** - 主要校验逻辑
2. **ResponseFieldProxy** - 响应字段代理访问
3. **异常处理分层** - 区分关键异常和运行时异常
4. **逐条执行机制** - 独立执行每条校验脚本


## 💼 详细使用说明

### 1️⃣ **Python 脚本校验**

#### **基础断言**

```yaml
script:
  - assert status_code == 200
  - assert content.success is True
  - assert len(content.token) == 16
  - assert content.user_id > 0
```

#### **条件判断**

```yaml
script:
  - assert status_code in [200, 201, 202]
  - assert content.status in ["active", "pending"]
  - assert len(content.items) > 0 and all(item.get("id") for item in content.items)
```

#### **多行脚本**

```yaml
script:
  # 使用 YAML 的 | 语法编写多行脚本
  - |
    if status_code == 200:
        assert content.success is True
    elif status_code == 400:
        assert content.error_code is not None
    else:
        assert False, f"Unexpected status code: {status_code}"
  
  # 循环校验
  - |
    for item in content.items:
        assert item.get("id") is not None
        assert item.get("name") is not None
```

#### **自定义错误信息**

```yaml
script:
  - assert status_code == 200, f"Expected 200, got {status_code}"
  - assert content.success is True, "API call should succeed"
  - assert len(content.token) == 16, f"Token length invalid: expected 16, got {len(content.token)}"
```

### 2️⃣ **自定义函数校验**

#### **函数定义**

在 `debugtalk.py` 中定义校验函数：

```python
def validate_token(token):
    """验证token格式"""
    if len(token) != 16:
        raise ValueError(f"Token length should be 16, got {len(token)}")
    if not token.isalnum():
        raise ValueError("Token should be alphanumeric")
    return True

def validate_user_info(user_data):
    """验证用户信息完整性"""
    required_fields = ["id", "name", "email"]
    for field in required_fields:
        if field not in user_data:
            raise AssertionError(f"Missing required field: {field}")
    return True

def check_response_time(elapsed_seconds):
    """检查响应时间"""
    if elapsed_seconds >= 2.0:
        raise ValueError(f"Response time too slow: {elapsed_seconds}s")
    return True
```

#### **函数调用**

```yaml
script:
  # 直接调用函数，函数返回值作为输出显示
  - ${validate_token(content.token)}
  - ${validate_user_info(content.user)}
  - ${check_response_time(elapsed.total_seconds)}
  
  # 结合assert使用（推荐）
  - assert ${validate_token(content.token)} is True
  - assert ${validate_user_info(content.user)} is True
```

#### **参数传递**

```yaml
script:
  # 传递单个参数
  - ${validate_token($token)}
  - ${validate_token(content.token)}
  
  # 传递多个参数
  - ${validate_signature($device_sn, $os_platform, $app_version)}
  
  # 传递列表参数
  - ${validate_list_data([$device_sn, $os_platform, $app_version])}
  
  # 传递字典参数
  - ${validate_dict_data({device_sn: $device_sn, platform: $os_platform})}
  
  # 传递复杂对象
  - ${validate_response_data(content)}
```

### 3️⃣ **变量引用**

#### **测试变量引用**

```yaml
variables:
  expected_status: 200
  expected_token_length: 16

script:
  - assert status_code == $expected_status
  - assert len(content.token) == $expected_token_length
```

#### **提取变量引用**

```yaml
extract:
  - user_id: content.user.id
  - token: content.token

script:
  - assert $user_id > 0
  - assert len("$token") == 16  # 字符串形式的变量引用需要加引号
  - ${validate_token($token)}
```

### 4️⃣ **错误处理**

#### **容错机制**

当某条脚本校验失败时，系统会：

1. **记录详细错误信息**
2. **继续执行后续脚本**
3. **在测试报告中显示失败详情**

```yaml
script:
  - assert status_code == 200        # 通过
  - assert content.invalid_field == "test"  # 失败，但不中断后续校验
  - assert content.success is True   # 继续执行
  - ${validate_token(content.token)} # 继续执行
```

#### **异常类型说明**

- **AssertionError** - assert 语句失败
- **NameError** - 变量不存在
- **AttributeError** - 属性访问错误
- **TypeError** - 类型错误
- **ValueError** - 值错误（自定义函数常用）
- **SyntaxError** - 语法错误

### 5️⃣ **高级用法**

#### **响应字段深度访问**

```yaml
script:
  # 嵌套数据访问
  - assert content.user.profile.age > 0
  - assert len(content.user.permissions) > 0
  
  # 数组访问
  - assert len(content.items) > 0
  - assert content.items[0].id is not None
  
  # 字典访问
  - assert headers["Content-Type"] == "application/json"
  - assert "Authorization" in headers
```

#### **动态校验**

```yaml
script:
  # 根据响应内容动态校验
  - |
    if content.user.type == "vip":
        assert content.user.vip_level > 0
        assert content.user.vip_expires is not None
    else:
        assert content.user.vip_level == 0
```

#### **批量校验**

```yaml
script:
  # 校验数组中的每个元素
  - |
    for item in content.products:
        assert item.get("id") is not None
        assert item.get("price") > 0
        assert item.get("status") in ["active", "inactive"]
```

### 6️⃣ **最佳实践**

#### 1. **模块化校验函数** - 将复杂逻辑封装到 debugtalk.py 中

```python
# debugtalk.py
def validate_user_data(user):
    """用户数据校验"""
    validate_required_fields(user, ["id", "name", "email"])
    validate_user_id(user["id"])
    validate_email_format(user["email"])
    return True

def validate_required_fields(data, fields):
    """必填字段校验"""
    for field in fields:
        assert field in data, f"Missing required field: {field}"
        assert data[field] is not None, f"Field '{field}' cannot be None"

def validate_user_id(user_id):
    """用户ID校验"""
    assert isinstance(user_id, int), f"User ID must be integer, got {type(user_id)}"
    assert user_id > 0, f"User ID must be positive, got {user_id}"

def validate_email_format(email):
    """邮箱格式校验"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    assert re.match(pattern, email), f"Invalid email format: {email}"

def validate_api_response(response_data):
    """
    API响应校验的最佳实践
    
    Args:
        response_data: 响应数据
        
    Returns:
        bool: 校验结果
        
    Raises:
        AssertionError: 校验失败时抛出详细错误信息
    """
    # 使用断言提供清晰的错误信息
    assert "code" in response_data, "Response missing 'code' field"
    assert "message" in response_data, "Response missing 'message' field"
    
    # 业务逻辑检查
    if response_data["code"] == 0:
        assert "data" in response_data, "Success response missing 'data' field"
        assert response_data["data"] is not None, "Success response data is None"
    
    return True
```

#### 2. **清晰的错误信息** - 使用自定义assert消息

```yaml
script:
  # 提供清晰的错误信息
  - assert status_code == 200, f"Expected status 200, got {status_code}"
  - assert content.success is True, f"API call failed: {content.get('message', 'Unknown error')}"
  - assert len(content.token) == 16, f"Token length invalid: expected 16, got {len(content.token)}"
```

#### 3. **脚本组织** - 避免在YAML中写过程的脚本，同时确保脚本来源可信

```yaml
script:
  # 基础校验
  - assert status_code == 200
  - assert content.success is True
  
  # 数据完整性校验
  - ${validate_required_fields(content, ["id", "name", "email"])}
  
  # 业务逻辑校验
  - ${validate_business_rules(content)}
  
  # 性能校验
  - assert elapsed.total_seconds < 2.0
```

### 7️⃣  **完整示例**

```yaml
config:
  name: "用户API测试"
  variables:
    expected_status: 200
    min_token_length: 16

teststeps:
- name: 获取用户信息
  request:
    url: /api/user/profile
    method: GET
  extract:
    - user_id: content.user.id
    - token: content.token
  script:
    # 基础校验
    - assert status_code == $expected_status
    - assert content.success is True
    - assert content.message == "success"
    
    # 数据校验
    - assert content.user is not None
    - assert content.user.id > 0
    - assert len(content.token) >= $min_token_length
    
    # 自定义函数校验
    - ${validate_user_data(content.user)}
    - ${validate_token_format(content.token)}
    - assert ${check_permissions(content.user.permissions)} is True
    
    # 复杂条件校验
    - |
      if content.user.vip_level > 0:
          assert content.user.vip_expires is not None
      else:
          assert content.user.vip_expires is None
```



## 🏆 **总结**

| 特性         | 传统 validate  | script 校验    |
|-------------|---------------|----------------|
| 学习成本     | 需要记忆特定语法 | 标准Python语法  |
| 灵活性       | 固定格式       | 任意Python脚本  |
| 错误处理     | 单点失败中断    | 逐条执行，容错处理|
| 自定义函数   | 有限支持        | 完全支持        |
| 复杂逻辑     | 有限支持       | 支持条件、循环等  |
| 调试能力     | 基础           | 强大（逐条结果）  |
| 数据校验能力  | 不通用且结果单一 | 自定义任意结果   |

通过以上功能，`script` 提供了比传统 `validate` 更加灵活和强大的校验能力，特别适合复杂的业务逻辑校验场景，而且完美地平衡了**简单性**和**强大性**

- ✅ **简单直观** - 使用标准Python语法，零学习成本
- ✅ **功能强大** - 支持任意复杂的校验逻辑
- ✅ **设计精良** - 逐条执行、智能异常处理、详细报告
- ✅ **实现完整** - 从解析、执行到报告的完整流程
- ✅ **用户友好** - 与assert一脉相承，符合开发者直觉