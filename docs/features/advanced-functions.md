# 自定义函数高级用法

本文档详细介绍 ApiMeter 中自定义函数的高级参数传递功能，包括列表参数、字典参数、嵌套对象参数以及通配符批量校验等强大特性。

## 📚 目录

- [为什么需要高级参数解析？](#为什么需要高级参数解析)
- [1. 基础回顾](#1-基础回顾)
- [2. 链式取值](#2-链式取值)
- [3. 列表参数解析](#3-列表参数解析)
- [4. 字典对象参数解析](#4-字典对象参数解析)
- [5. 复杂嵌套对象参数](#5-复杂嵌套对象参数)
- [6. 通配符批量校验](#6-通配符批量校验)
- [7. 正则表达式校验](#7-正则表达式校验)
- [8. 类型校验](#8-类型校验)
- [9. 综合实战案例](#9-综合实战案例)
- [10. 最佳实践](#10-最佳实践)

## 为什么需要高级参数解析？

### 实际场景的复杂性

在实际 API 测试中，我们常常遇到以下复杂场景：

**场景 1：签名生成**
```python
# 需要将多个参数组合生成签名
sign = md5(device_sn + os_platform + app_version + timestamp)
```

**场景 2：批量数据校验**
```json
{
  "products": [
    {"id": 1, "sku": [{"id": "A", "price": 100}, {"id": "B", "price": 200}]},
    {"id": 2, "sku": [{"id": "C", "price": 150}, {"id": "D", "price": 250}]}
  ]
}
```
需要校验所有 sku 中的 id 和 price 字段。

**场景 3：复杂配置传递**
```python
# 需要传递复杂的配置对象
validate_data(response, {
    "list_path": "products",
    "nested_field": "sku",
    "check_fields": ["id", "price", "currency"]
})
```

传统的参数传递方式无法优雅地处理这些场景，ApiMeter 的高级参数解析功能完美解决了这些问题。

## 1. 基础回顾

### 1.1 简单参数传递

最基础的用法，传递单个参数：

```yaml
# debugtalk.py
def validate_token(token):
    assert len(token) == 16, f"Token length should be 16, got {len(token)}"
    return True

# 测试用例
script:
  - ${validate_token(content.token)}
```

### 1.2 多个参数传递

传递多个独立参数：

```yaml
# debugtalk.py
def get_sign(device_sn, os_platform, app_version):
    content = f"{device_sn}{os_platform}{app_version}"
    return hashlib.md5(content.encode()).hexdigest()

# 测试用例
request:
  json:
    sign: ${get_sign($device_sn, $os_platform, $app_version)}
```

## 2. 链式取值

### 2.1 全局变量链式取值

直接访问响应数据的深层字段：

```yaml
# debugtalk.py
def validate_user_name(name):
    assert len(name) > 0, "User name cannot be empty"
    return True

# 测试用例 - 链式访问
script:
  # 访问 content.data.user.profile.name
  - ${validate_user_name(content.data.user.profile.name)}
```

**响应数据示例：**
```json
{
  "data": {
    "user": {
      "profile": {
        "name": "Alice",
        "age": 25
      }
    }
  }
}
```

### 2.2 自定义变量链式取值

提取变量后支持链式访问：

```yaml
extract:
  - user_info: content.data.user

script:
  # 使用提取的变量进行链式访问
  - ${validate_user_name($user_info.profile.name)}
```

### 2.3 数组索引访问

```yaml
script:
  # 访问数组第一个元素的字段
  - ${validate_price(content.products[0].price)}
  
  # 访问嵌套数组
  - ${validate_sku_id(content.products[0].sku[0].id)}
```

## 3. 列表参数解析

### 3.1 基本语法

使用中括号 `[]` 传递列表参数：

```yaml
${function_name([$param1, $param2, $param3])}
```

### 3.2 使用场景：签名生成

**场景描述**：
API 需要将多个参数组合后生成签名，传统方式需要逐个传递参数，使用列表参数可以更简洁。

**debugtalk.py**：
```python
import hashlib
import hmac

SECRET_KEY = "DebugTalk"

def get_sign_v2(args_list):
    """
    使用列表参数生成签名
    
    Args:
        args_list: 参数列表，如 ["device_001", "ios", "2.8.6"]
    
    Returns:
        签名字符串
    """
    content = "".join(args_list).encode("ascii")
    sign_key = SECRET_KEY.encode("ascii")
    sign = hmac.new(sign_key, content, hashlib.sha1).hexdigest()
    return sign
```

**测试用例**：
```yaml
config:
  variables:
    device_sn: "TEST_DEVICE_001"
    os_platform: "ios"
    app_version: "2.8.6"

teststeps:
- name: 获取访问令牌
  request:
    url: /api/get-token
    method: POST
    json:
      # 使用列表参数传递
      sign: ${get_sign_v2([$device_sn, $os_platform, $app_version])}
  script:
    - assert status_code == 200
```

### 3.3 使用场景：批量校验

**场景描述**：
需要同时校验多个字段是否存在。

**debugtalk.py**：
```python
def check_fields_exist(data, fields_list):
    """
    批量检查字段是否存在
    
    Args:
        data: 数据对象
        fields_list: 字段列表，如 ["id", "name", "email"]
    
    Returns:
        True if all fields exist
    """
    for field in fields_list:
        assert field in data, f"Missing required field: {field}"
    return True
```

**测试用例**：
```yaml
script:
  # 批量检查用户必填字段
  - ${check_fields_exist(content.user, [id, name, email, phone])}
  
  # 批量检查产品必填字段
  - ${check_fields_exist(content.product, [id, title, price, stock])}
```

### 3.4 列表参数 + 变量引用

```yaml
variables:
  required_user_fields: ["id", "name", "email"]
  required_product_fields: ["id", "title", "price"]

script:
  # 引用变量列表
  - ${check_fields_exist(content.user, $required_user_fields)}
  - ${check_fields_exist(content.product, $required_product_fields)}
```

## 4. 字典对象参数解析

### 4.1 基本语法

使用花括号 `{}` 传递字典参数：

```yaml
${function_name({key1: value1, key2: value2})}
```

**注意**：字典参数通常需要用引号包裹：

```yaml
"${function_name({key1: value1, key2: value2})}"
```

### 4.2 使用场景：复杂签名配置

**场景描述**：
签名算法需要多个参数，使用字典可以让参数更有语义。

**debugtalk.py**：
```python
import hashlib
import hmac

SECRET_KEY = "DebugTalk"

def get_sign_v3(args_dict):
    """
    使用字典参数生成签名
    
    Args:
        args_dict: 参数字典，如 {
            "device_sn": "xxx",
            "os_platform": "ios",
            "app_version": "2.8.6"
        }
    
    Returns:
        签名字符串
    """
    content = "".join([
        args_dict["device_sn"],
        args_dict["os_platform"],
        args_dict["app_version"]
    ]).encode("ascii")
    sign_key = SECRET_KEY.encode("ascii")
    sign = hmac.new(sign_key, content, hashlib.sha1).hexdigest()
    return sign
```

**测试用例**：
```yaml
request:
  json:
    # 使用字典参数（注意外层引号）
    sign: "${get_sign_v3({
      device_sn: $device_sn,
      os_platform: $os_platform,
      app_version: $app_version
    })}"
```

### 4.3 使用场景：配置对象传递

**场景描述**：
数据校验需要复杂的配置信息。

**debugtalk.py**：
```python
def validate_with_config(data, config):
    """
    根据配置校验数据
    
    Args:
        data: 待校验数据
        config: 配置对象，如 {
            "min_length": 10,
            "max_length": 100,
            "allow_empty": false
        }
    
    Returns:
        True if validation passes
    """
    min_len = config.get("min_length", 0)
    max_len = config.get("max_length", float('inf'))
    allow_empty = config.get("allow_empty", False)
    
    if not allow_empty:
        assert len(data) > 0, "Data cannot be empty"
    
    assert min_len <= len(data) <= max_len, \
        f"Data length {len(data)} not in range [{min_len}, {max_len}]"
    
    return True
```

**测试用例**：
```yaml
script:
  # 传递配置对象
  - "${validate_with_config(content.description, {
      min_length: 10,
      max_length: 500,
      allow_empty: false
    })}"
```

## 5. 复杂嵌套对象参数

### 5.1 使用场景：嵌套列表批量校验

**场景描述**：
响应数据包含多层嵌套结构，需要批量校验所有嵌套数据的特定字段。

**响应数据结构**：
```json
{
  "productList": [
    {
      "id": 1,
      "name": "Product 1",
      "sku": [
        {"id": "A", "amount": 100, "currency": "USD"},
        {"id": "B", "amount": 200, "currency": "USD"}
      ]
    },
    {
      "id": 2,
      "name": "Product 2",
      "sku": [
        {"id": "C", "amount": 150, "currency": "EUR"},
        {"id": "D", "amount": 250, "currency": "EUR"}
      ]
    }
  ]
}
```

**debugtalk.py**：
```python
def check_nested_list_fields(data, config):
    """
    检查嵌套列表中的字段
    
    Args:
        data: 响应数据
        config: 配置对象 {
            "list_path": "productList",        # 外层列表路径
            "nested_field": "sku",             # 内层列表字段名
            "check_fields": ["id", "amount"]   # 需要检查的字段
        }
    
    Returns:
        True if all validations pass
    """
    list_path = config["list_path"]
    nested_field = config["nested_field"]
    check_fields = config["check_fields"]
    
    # 获取外层列表
    items = data.get(list_path, [])
    assert len(items) > 0, f"List '{list_path}' is empty"
    
    # 遍历外层列表
    for item in items:
        # 获取内层列表
        nested_items = item.get(nested_field, [])
        assert len(nested_items) > 0, \
            f"Nested field '{nested_field}' is empty in item {item.get('id')}"
        
        # 遍历内层列表，检查字段
        for nested_item in nested_items:
            for field in check_fields:
                assert field in nested_item, \
                    f"Field '{field}' not found in nested item"
                assert nested_item[field] is not None, \
                    f"Field '{field}' is None"
    
    return True
```

**测试用例**：
```yaml
script:
  # 检查嵌套列表中的字段
  - "${check_nested_list_fields(content, {
      list_path: productList,
      nested_field: sku,
      check_fields: [id, amount, currency]
    })}"
```

### 5.2 使用场景：多级配置对象

**debugtalk.py**：
```python
def validate_complex_data(data, validation_rules):
    """
    使用复杂规则验证数据
    
    Args:
        data: 待验证数据
        validation_rules: 验证规则 {
            "user": {
                "required_fields": ["id", "name"],
                "name_min_length": 2
            },
            "product": {
                "required_fields": ["id", "price"],
                "price_min": 0
            }
        }
    """
    # 验证 user 数据
    if "user" in validation_rules:
        user_rules = validation_rules["user"]
        user_data = data.get("user", {})
        
        # 检查必填字段
        for field in user_rules.get("required_fields", []):
            assert field in user_data, f"User missing field: {field}"
        
        # 检查名称长度
        if "name_min_length" in user_rules:
            min_len = user_rules["name_min_length"]
            assert len(user_data.get("name", "")) >= min_len
    
    # 验证 product 数据
    if "product" in validation_rules:
        product_rules = validation_rules["product"]
        product_data = data.get("product", {})
        
        # 检查必填字段
        for field in product_rules.get("required_fields", []):
            assert field in product_data, f"Product missing field: {field}"
        
        # 检查价格
        if "price_min" in product_rules:
            price_min = product_rules["price_min"]
            assert product_data.get("price", -1) >= price_min
    
    return True
```

**测试用例**：
```yaml
script:
  # 传递多级配置对象
  - "${validate_complex_data(content, {
      user: {
        required_fields: [id, name, email],
        name_min_length: 2
      },
      product: {
        required_fields: [id, price, stock],
        price_min: 0
      }
    })}"
```

## 6. 通配符批量校验

### 6.1 通配符 `*` 语法

使用 `*` 通配符可以匹配任意层级的数据，实现批量校验。

**语法**：
```
path.to.*.field
path.to.*.nested.*.field
```

### 6.2 单层通配符

**场景**：校验所有产品的 ID 和价格。

**响应数据**：
```json
{
  "products": [
    {"id": 1, "price": 100},
    {"id": 2, "price": 200},
    {"id": 3, "price": 300}
  ]
}
```

**debugtalk.py**：
```python
def check(data, *field_paths):
    """
    通用字段检查函数
    支持通配符路径
    
    Args:
        data: 响应数据
        *field_paths: 字段路径列表，支持通配符
            如: "products.*.id", "products.*.price"
    """
    for path in field_paths:
        _check_field_path(data, path)
    return True

def _check_field_path(data, path):
    """检查单个字段路径"""
    parts = path.split('.')
    _recursive_check(data, parts)

def _recursive_check(data, parts):
    """递归检查字段"""
    if not parts:
        # 路径检查完毕，确保数据不为 None
        assert data is not None, "Field value is None"
        return
    
    part = parts[0]
    remaining = parts[1:]
    
    if part == '*':
        # 通配符：遍历列表或字典
        if isinstance(data, list):
            for item in data:
                _recursive_check(item, remaining)
        elif isinstance(data, dict):
            for value in data.values():
                _recursive_check(value, remaining)
    else:
        # 普通字段
        if isinstance(data, dict):
            assert part in data, f"Field '{part}' not found"
            _recursive_check(data[part], remaining)
        else:
            raise ValueError(f"Cannot access field '{part}' on non-dict data")
```

**测试用例**：
```yaml
script:
  # 检查所有产品的 id 和 price
  - ${check(content, products.*.id, products.*.price)}
```

### 6.3 多层通配符

**场景**：校验所有产品的所有 SKU 的字段。

**响应数据**：
```json
{
  "products": [
    {
      "id": 1,
      "sku": [
        {"id": "A", "amount": 100, "currency": "USD"},
        {"id": "B", "amount": 200, "currency": "USD"}
      ]
    },
    {
      "id": 2,
      "sku": [
        {"id": "C", "amount": 150, "currency": "EUR"}
      ]
    }
  ]
}
```

**测试用例**：
```yaml
script:
  # 检查所有产品的所有 SKU 的字段
  - ${check(content,
      products.*.id,
      products.*.sku.*.id,
      products.*.sku.*.amount,
      products.*.sku.*.currency
    )}
```

### 6.4 通配符 + 链式取值

```yaml
script:
  # 检查嵌套深层数据
  - ${check(content,
      data.product.purchasePlan.*.sku.*.id,
      data.product.purchasePlan.*.sku.*.amount,
      data.product.purchasePlan.*.sku.*.origin_amount,
      data.product.purchasePlan.*.sku.*.currency,
      data.product.purchasePlan.*.sku.*.duration
    )}
```

## 7. 正则表达式校验

### 7.1 正则表达式语法 `~=`

使用 `~=` 操作符进行正则表达式匹配。

**语法**：
```
'field_name ~= regex_pattern'
```

### 7.2 使用场景：URL 格式校验

**debugtalk.py**（扩展 check 函数）：
```python
import re

def check(data, *rules):
    """
    通用检查函数
    支持：
    - 通配符路径: "products.*.id"
    - 正则表达式: "_url ~= ^https?://.*"
    - 包含校验: "status =* [active, pending]"
    - 类型校验: "user @= dict"
    """
    for rule in rules:
        if isinstance(rule, str) and ' ~= ' in rule:
            # 正则表达式校验
            field, pattern = rule.split(' ~= ')
            field = field.strip()
            pattern = pattern.strip()
            _check_regex(data, field, pattern)
        else:
            # 普通字段路径校验
            _check_field_path(data, rule)
    return True

def _check_regex(data, field, pattern):
    """正则表达式校验"""
    value = _get_field_value(data, field)
    assert re.match(pattern, str(value)), \
        f"Field '{field}' value '{value}' does not match pattern '{pattern}'"
```

**测试用例**：
```yaml
script:
  # URL 格式校验
  - ${check(content,
      '_url ~= ^https?://[^\s/$.?#].[^\s]*$'
    )}
  
  # 邮箱格式校验
  - ${check(content,
      'user.email ~= ^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )}
  
  # 电话号码格式校验
  - ${check(content,
      'user.phone ~= ^1[3-9]\d{9}$'
    )}
```

## 8. 类型校验

### 8.1 类型校验语法 `@=`

使用 `@=` 操作符进行类型校验。

**语法**：
```
'field_name @= type_name'
```

**支持的类型**：
- `dict` - 字典类型
- `list` - 列表类型
- `str` - 字符串类型
- `int` - 整数类型
- `float` - 浮点数类型
- `bool` - 布尔类型

### 8.2 使用场景：数据结构校验

**debugtalk.py**（继续扩展 check 函数）：
```python
def check(data, *rules):
    """通用检查函数"""
    for rule in rules:
        if isinstance(rule, str):
            if ' ~= ' in rule:
                # 正则表达式
                field, pattern = rule.split(' ~= ')
                _check_regex(data, field.strip(), pattern.strip())
            elif ' =* ' in rule:
                # 包含校验
                field, values = rule.split(' =* ')
                _check_contains(data, field.strip(), values.strip())
            elif ' @= ' in rule:
                # 类型校验
                field, type_name = rule.split(' @= ')
                _check_type(data, field.strip(), type_name.strip())
            else:
                # 字段路径
                _check_field_path(data, rule)
        else:
            _check_field_path(data, rule)
    return True

def _check_type(data, field, type_name):
    """类型校验"""
    value = _get_field_value(data, field)
    
    type_map = {
        'dict': dict,
        'list': list,
        'str': str,
        'int': int,
        'float': float,
        'bool': bool
    }
    
    expected_type = type_map.get(type_name)
    assert expected_type, f"Unknown type: {type_name}"
    assert isinstance(value, expected_type), \
        f"Field '{field}' type is {type(value).__name__}, expected {type_name}"
```

**测试用例**：
```yaml
script:
  # 类型校验
  - ${check(content,
      'user @= dict',
      'user.id @= int',
      'user.name @= str',
      'user.is_active @= bool',
      'products @= list'
    )}
```

### 8.3 包含校验语法 `=*`

使用 `=*` 操作符检查值是否在指定范围内。

**语法**：
```
'field_name =* [value1, value2, value3]'
```

**debugtalk.py**（check 函数已包含）：
```python
def _check_contains(data, field, values_str):
    """包含校验"""
    # 解析值列表: "[USD, CNY, EUR]" -> ["USD", "CNY", "EUR"]
    values_str = values_str.strip('[]')
    expected_values = [v.strip() for v in values_str.split(',')]
    
    value = _get_field_value(data, field)
    assert str(value) in expected_values, \
        f"Field '{field}' value '{value}' not in {expected_values}"
```

**测试用例**：
```yaml
script:
  # 货币类型校验
  - ${check(content,
      'default_currency =* [USD, CNY, EUR]'
    )}
  
  # 状态校验
  - ${check(content,
      'order.status =* [pending, processing, completed, cancelled]'
    )}
```

## 9. 综合实战案例

### 案例 1：电商 API 完整校验

**响应数据**：
```json
{
  "_url": "https://api.example.com/products",
  "default_currency": "USD",
  "default_sku": {
    "id": "DEFAULT_001",
    "price": 99.99
  },
  "product": {
    "id": 123,
    "name": "Product Name",
    "purchasePlan": [
      {
        "plan_id": "PLAN_001",
        "sku": [
          {
            "id": "SKU_001",
            "amount": 100,
            "origin_amount": 120,
            "currency": "USD",
            "duration": 30
          },
          {
            "id": "SKU_002",
            "amount": 200,
            "origin_amount": 240,
            "currency": "USD",
            "duration": 60
          }
        ]
      }
    ]
  }
}
```

**测试用例**：
```yaml
script:
  # 一次性校验所有字段
  - ${check(content,
      '_url ~= ^https?://[^\s/$.?#].[^\s]*$',
      'default_currency =* [USD, CNY, EUR]',
      'default_sku @= dict',
      'product @= dict',
      'product.purchasePlan @= list',
      product.purchasePlan.*.sku.*.id,
      product.purchasePlan.*.sku.*.amount,
      product.purchasePlan.*.sku.*.origin_amount,
      product.purchasePlan.*.sku.*.currency,
      product.purchasePlan.*.sku.*.duration
    )}
```

### 案例 2：用户信息复杂校验

**debugtalk.py**：
```python
def validate_user_complete(user_data, rules):
    """
    用户信息完整校验
    
    Args:
        user_data: 用户数据
        rules: 校验规则 {
            "required_fields": ["id", "name", "email"],
            "email_pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
            "name_min_length": 2,
            "name_max_length": 50,
            "check_permissions": true,
            "required_permissions": ["read", "write"]
        }
    """
    import re
    
    # 检查必填字段
    for field in rules.get("required_fields", []):
        assert field in user_data, f"Missing required field: {field}"
        assert user_data[field] is not None, f"Field '{field}' is None"
    
    # 检查邮箱格式
    if "email_pattern" in rules and "email" in user_data:
        pattern = rules["email_pattern"]
        email = user_data["email"]
        assert re.match(pattern, email), f"Invalid email format: {email}"
    
    # 检查名称长度
    if "name" in user_data:
        name = user_data["name"]
        min_len = rules.get("name_min_length", 0)
        max_len = rules.get("name_max_length", float('inf'))
        assert min_len <= len(name) <= max_len, \
            f"Name length {len(name)} not in range [{min_len}, {max_len}]"
    
    # 检查权限
    if rules.get("check_permissions", False):
        required_perms = rules.get("required_permissions", [])
        user_perms = user_data.get("permissions", [])
        for perm in required_perms:
            assert perm in user_perms, f"Missing permission: {perm}"
    
    return True
```

**测试用例**：
```yaml
script:
  - "${validate_user_complete(content.user, {
      required_fields: [id, name, email, phone],
      email_pattern: '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
      name_min_length: 2,
      name_max_length: 50,
      check_permissions: true,
      required_permissions: [read, write, delete]
    })}"
```

### 案例 3：多环境配置签名

**debugtalk.py**：
```python
import hashlib
import hmac
import time

def generate_signature(params):
    """
    生成请求签名
    
    Args:
        params: 签名参数 {
            "method": "POST",
            "url": "/api/users",
            "timestamp": 1234567890,
            "nonce": "random_string",
            "body": {...},
            "secret_key": "xxx"
        }
    """
    # 按key排序
    sorted_params = sorted([
        (k, v) for k, v in params.items() 
        if k != 'secret_key'
    ])
    
    # 拼接字符串
    sign_str = '&'.join([f"{k}={v}" for k, v in sorted_params])
    
    # 生成签名
    secret = params.get("secret_key", "").encode('utf-8')
    sign = hmac.new(secret, sign_str.encode('utf-8'), hashlib.sha256).hexdigest()
    
    return sign

def get_timestamp():
    """获取当前时间戳"""
    return int(time.time())

def get_nonce():
    """生成随机字符串"""
    import random
    import string
    return ''.join(random.choices(string.ascii_letters + string.digits, k=16))
```

**测试用例**：
```yaml
variables:
  secret_key: "MySecretKey123"
  request_method: "POST"
  request_url: "/api/users"

teststeps:
- name: 创建用户（带签名）
  request:
    url: $base_url$request_url
    method: POST
    headers:
      X-Timestamp: ${get_timestamp()}
      X-Nonce: ${get_nonce()}
      X-Signature: "${generate_signature({
        method: $request_method,
        url: $request_url,
        timestamp: ${get_timestamp()},
        nonce: ${get_nonce()},
        body: {name: 'Alice', email: 'alice@example.com'},
        secret_key: $secret_key
      })}"
    json:
      name: "Alice"
      email: "alice@example.com"
```

## 10. 最佳实践

### 10.1 参数命名规范

**推荐**：
```python
# ✅ 清晰的参数名
def validate_user_data(user_data, validation_rules):
    pass

def check_nested_fields(response_data, field_config):
    pass
```

**不推荐**：
```python
# ❌ 模糊的参数名
def validate(data, rules):
    pass

def check(a, b):
    pass
```

### 10.2 函数职责单一

**推荐**：
```python
# ✅ 职责单一
def validate_email_format(email):
    """只验证邮箱格式"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    assert re.match(pattern, email), f"Invalid email: {email}"
    return True

def validate_required_fields(data, fields):
    """只验证必填字段"""
    for field in fields:
        assert field in data, f"Missing field: {field}"
    return True
```

**不推荐**：
```python
# ❌ 职责混乱
def validate_everything(data, config):
    """做太多事情"""
    # 验证格式
    # 验证字段
    # 验证类型
    # 验证业务逻辑
    # ...
    pass
```

### 10.3 提供清晰的错误信息

**推荐**：
```python
# ✅ 清晰的错误信息
def validate_price(price):
    assert isinstance(price, (int, float)), \
        f"Price must be number, got {type(price).__name__}"
    assert price >= 0, \
        f"Price must be non-negative, got {price}"
    assert price <= 1000000, \
        f"Price must be less than 1000000, got {price}"
    return True
```

**不推荐**：
```python
# ❌ 模糊的错误信息
def validate_price(price):
    assert isinstance(price, (int, float)), "Invalid type"
    assert price >= 0, "Invalid value"
    assert price <= 1000000, "Too large"
    return True
```

### 10.4 合理使用通配符

**推荐**：
```yaml
# ✅ 通配符配合具体字段
script:
  # 先检查基本结构
  - assert isinstance(content.products, list)
  - assert len(content.products) > 0
  
  # 再使用通配符批量检查
  - ${check(content,
      products.*.id,
      products.*.price
    )}
```

**不推荐**：
```yaml
# ❌ 过度依赖通配符
script:
  # 直接使用通配符，错误信息不明确
  - ${check(content, products.*.*.*)}
```

### 10.5 文档注释

**推荐**：
```python
def check_nested_list_fields(data, config):
    """
    检查嵌套列表中的字段
    
    Args:
        data (dict): 响应数据
        config (dict): 配置对象
            - list_path (str): 外层列表路径
            - nested_field (str): 内层列表字段名
            - check_fields (list): 需要检查的字段列表
    
    Returns:
        bool: 校验是否通过
    
    Raises:
        AssertionError: 当校验失败时
    
    Example:
        >>> check_nested_list_fields(response, {
        ...     "list_path": "products",
        ...     "nested_field": "sku",
        ...     "check_fields": ["id", "price"]
        ... })
    """
    pass
```

### 10.6 性能考虑

**通配符批量校验**：
- ✅ 适合：数据量 < 1000 条
- ⚠️ 注意：数据量 1000-10000 条
- ❌ 不推荐：数据量 > 10000 条（考虑抽样校验）

**抽样校验示例**：
```python
def check_large_list(data, field_path, sample_size=100):
    """
    大列表抽样校验
    
    Args:
        data: 数据
        field_path: 字段路径
        sample_size: 抽样数量
    """
    import random
    
    items = _get_field_value(data, field_path)
    assert isinstance(items, list), "Field must be a list"
    
    # 如果数据量小，全量检查
    if len(items) <= sample_size:
        check_items = items
    else:
        # 大数据量，随机抽样
        check_items = random.sample(items, sample_size)
    
    # 校验抽样数据
    for item in check_items:
        assert item is not None
        # 其他校验逻辑...
    
    return True
```

## 📝 总结

ApiMeter 的自定义函数高级参数支持让 API 测试变得更加灵活和强大：

| 特性 | 使用场景 | 优势 |
|-----|---------|------|
| 列表参数 | 签名生成、批量校验 | 简化参数传递 |
| 字典参数 | 复杂配置传递 | 语义清晰 |
| 嵌套对象 | 多层数据校验 | 功能强大 |
| 通配符 `*` | 批量字段校验 | 高效便捷 |
| 正则 `~=` | 格式校验 | 灵活匹配 |
| 类型 `@=` | 数据结构校验 | 类型安全 |
| 包含 `=*` | 枚举值校验 | 范围检查 |

**下一步学习**：
- [全局变量完整指南](global-variables.md)
- [高级用法示例](../examples/advanced-examples.md)
- [自定义脚本校验](../prepare/script.md)

---

**有问题？** 查看 [FAQ](../FAQ.md) 或 [提交 Issue](https://git.umlife.net/utils/apimeter/issues)

