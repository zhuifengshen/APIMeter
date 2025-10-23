# 全局变量完整指南

ApiMeter 提供了强大的全局变量系统，让你可以在 `script` 脚本中直接访问响应数据，无需特殊语法。本文档详细介绍所有可用的全局变量及其高级用法。

## 📚 目录

- [什么是全局变量？](#什么是全局变量)
- [可用的全局变量列表](#可用的全局变量列表)
- [链式取值详解](#链式取值详解)
- [变量转义功能](#变量转义功能)
- [全局变量 vs 自定义变量](#全局变量-vs-自定义变量)
- [常见使用场景](#常见使用场景)
- [最佳实践](#最佳实践)
- [常见问题](#常见问题)

## 什么是全局变量？

**全局变量** 是 ApiMeter 在 `script` 脚本执行时自动注入的响应相关变量。你可以直接在脚本中使用这些变量，无需任何前缀或特殊语法。

**对比传统方式：**

```yaml
# ❌ 传统 validate 方式
validate:
  - eq: ["status_code", 200]           # 需要用字符串表示
  - eq: ["content.token", "xxx"]       # 字段访问需要点号字符串

# ✅ ApiMeter script 方式
script:
  - assert status_code == 200          # 直接使用变量
  - assert content.token == "xxx"      # 支持对象属性访问
```

## 可用的全局变量列表

### 📊 响应状态相关

#### 1. `status_code`
**类型**：`int`  
**说明**：HTTP 响应状态码

**示例**：
```yaml
script:
  - assert status_code == 200
  - assert status_code in [200, 201, 202]
  - assert 200 <= status_code < 300, f"期望2xx状态码，实际: {status_code}"
```

---

#### 2. `ok`
**类型**：`bool`  
**说明**：请求是否成功（状态码 < 400）

**示例**：
```yaml
script:
  - assert ok is True
  - assert ok is True, "请求失败"
  
  # 条件判断
  - |
    if ok:
        assert content.success is True
    else:
        assert content.error_code is not None
```

---

#### 3. `reason`
**类型**：`str`  
**说明**：HTTP 状态码对应的原因短语

**示例**：
```yaml
script:
  - assert reason == "OK"              # 200 OK
  - assert reason == "Created"         # 201 Created
  - assert reason == "Not Found"       # 404 Not Found
```

---

#### 4. `url`
**类型**：`str`  
**说明**：实际请求的完整 URL（包含重定向后的 URL）

**示例**：
```yaml
script:
  - assert url.startswith("https://")
  - assert "api" in url
  - assert url.endswith("/users/1001")
```

---

### 📦 响应体相关

#### 5. `content`
**类型**：`dict-like` （ResponseFieldProxy）  
**说明**：响应内容，自动解析 JSON（最常用）

**示例**：
```yaml
script:
  # 基础访问
  - assert content.success is True
  - assert content.code == 0
  - assert content.message == "success"
  
  # 链式取值
  - assert content.data.user.name == "Alice"
  - assert content.data.user.profile.age > 18
  
  # 数组访问
  - assert len(content.items) > 0
  - assert content.items[0].id is not None
  
  # 字典访问
  - assert "token" in content
  - assert content["token"] is not None
```

---

#### 6. `body`
**类型**：`dict-like` （ResponseFieldProxy）  
**说明**：与 `content` 等价，原始响应体

**示例**：
```yaml
script:
  - assert body.success is True
  - assert "token" in body
```

---

#### 7. `json`
**类型**：`dict-like` （ResponseFieldProxy）  
**说明**：与 `content` 等价，JSON 响应内容

**示例**：
```yaml
script:
  - assert json.code == 0
  - assert json.data.user.name == "Alice"
```

---

#### 8. `text`
**类型**：`str`  
**说明**：响应的文本内容（未解析的原始字符串）

**示例**：
```yaml
script:
  - assert len(text) > 0
  - assert "success" in text
  - assert text.startswith("{")       # JSON 响应
  - assert text.startswith("<html")   # HTML 响应
```

---

### 📋 响应头相关

#### 9. `headers`
**类型**：`dict-like`  
**说明**：响应头信息

**示例**：
```yaml
script:
  # 访问响应头
  - assert headers["Content-Type"] == "application/json"
  - assert "Server" in headers
  
  # 大小写不敏感
  - assert headers["content-type"] == "application/json"
  - assert headers["Content-Type"] == headers["content-type"]
  
  # 常见响应头检查
  - assert "application/json" in headers["Content-Type"]
  - assert headers.get("Cache-Control") is not None
```

---

#### 10. `cookies`
**类型**：`dict-like`  
**说明**：Cookie 信息

**示例**：
```yaml
script:
  # 检查 Cookie 是否存在
  - assert "session_id" in cookies
  - assert cookies["session_id"] is not None
  
  # Cookie 值校验
  - assert len(cookies["session_id"]) > 0
  - assert cookies.get("user_id") is not None
```

---

### ⏱️ 性能相关

#### 11. `elapsed`
**类型**：`object` （timedelta）  
**说明**：请求响应时间对象

**示例**：
```yaml
script:
  # 响应时间校验（秒）
  - assert elapsed.total_seconds < 2.0
  - assert elapsed.total_seconds < 1.0, f"响应过慢: {elapsed.total_seconds}秒"
  
  # 毫秒级别
  - assert elapsed.total_seconds * 1000 < 500  # 500ms
  
  # 复杂条件
  - |
    response_time = elapsed.total_seconds
    if response_time > 2.0:
        print(f"警告：响应时间过长 {response_time}秒")
    assert response_time < 5.0, "响应超时"
```

---

### 🔧 编码相关

#### 12. `encoding`
**类型**：`str` 或 `None`  
**说明**：响应的字符编码

**示例**：
```yaml
script:
  - assert encoding == "utf-8"
  - assert encoding in ["utf-8", "UTF-8", None]
```

---

### 📡 完整响应对象

#### 13. `response`
**类型**：`Response` （requests.Response 对象）  
**说明**：完整的 requests Response 对象

**示例**：
```yaml
script:
  # 访问所有 Response 属性
  - assert response.status_code == 200
  - assert response.ok is True
  - assert response.headers["Content-Type"] == "application/json"
  
  # Response 对象方法
  - assert response.json()["success"] is True
  - assert len(response.content) > 0
```

---

## 链式取值详解

### 什么是链式取值？

链式取值允许你使用点号 `.` 访问嵌套的数据结构，类似于 JavaScript 中的对象属性访问。

### 基础链式取值

```yaml
script:
  # 一级访问
  - assert content.user is not None
  
  # 二级访问
  - assert content.user.name == "Alice"
  
  # 三级访问
  - assert content.user.profile.age > 18
  
  # 四级及更深
  - assert content.data.user.profile.contact.email == "alice@example.com"
```

**对应的数据结构：**
```json
{
  "data": {
    "user": {
      "profile": {
        "contact": {
          "email": "alice@example.com"
        }
      }
    }
  }
}
```

### 数组索引访问

```yaml
script:
  # 访问数组第一个元素
  - assert content.items[0].id is not None
  
  # 访问数组最后一个元素
  - assert content.items[-1].status == "completed"
  
  # 嵌套数组访问
  - assert content.users[0].orders[0].product_id == 123
```

**对应的数据结构：**
```json
{
  "items": [
    {"id": 1, "name": "Item 1"},
    {"id": 2, "name": "Item 2"}
  ],
  "users": [
    {
      "orders": [
        {"product_id": 123}
      ]
    }
  ]
}
```

### 混合访问

```yaml
script:
  # 对象 -> 数组 -> 对象 -> 字段
  - assert content.data.users[0].profile.name == "Alice"
  
  # 数组 -> 对象 -> 数组 -> 对象
  - assert content.orders[0].items[0].price > 0
```

### 链式取值的类型安全

```yaml
script:
  # ✅ 推荐：先检查存在性
  - assert content.user is not None
  - assert content.user.name == "Alice"
  
  # ✅ 推荐：使用条件判断
  - |
    if hasattr(content, 'user') and content.user:
        assert content.user.name == "Alice"
  
  # ⚠️ 注意：直接访问可能报错
  - assert content.non_existent_field.name == "Alice"  # AttributeError
```

## 变量转义功能

### 为什么需要变量转义？

当响应数据中的字段名与全局变量同名时，会产生歧义。

**问题场景：**
```json
{
  "data": {
    "content": "这是内容",       // 字段名叫 content
    "status_code": "SUCCESS"     // 字段名叫 status_code
  }
}
```

在自定义函数中：
```python
def check_field_exists(data, field_name):
    # 希望 field_name 是字符串 "content"
    # 但如果传递 content，会传递全局变量的值（整个响应体）
    return field_name in data
```

### 转义语法

使用反斜杠 `\` 将全局变量转义为字面量字符串：

```yaml
script:
  # content 是全局变量（整个响应体）
  # \content 是字符串 "content"（字段名）
  - ${check_field_exists(data, \content)}
  - ${check_field_exists(data, \status_code)}
```

### 支持转义的全局变量

所有全局变量都可以转义：
- `\content` → 字符串 `"content"`
- `\body` → 字符串 `"body"`
- `\text` → 字符串 `"text"`
- `\json` → 字符串 `"json"`
- `\status_code` → 字符串 `"status_code"`
- `\headers` → 字符串 `"headers"`
- `\cookies` → 字符串 `"cookies"`
- `\encoding` → 字符串 `"encoding"`
- `\ok` → 字符串 `"ok"`
- `\reason` → 字符串 `"reason"`
- `\url` → 字符串 `"url"`

### 完整示例

**debugtalk.py：**
```python
def check_data_not_null(data, field_count, field_prefix, field_name):
    """
    检查数据字段不为空
    
    Args:
        data: 数据对象
        field_count: 字段数量
        field_prefix: 字段前缀
        field_name: 字段名（需要转义）
    """
    # 假设数据结构: {"lines": "...", "content": "..."}
    for i in range(field_count):
        key = f"{field_prefix}{i}"
        assert key in data, f"Missing field: {key}"
    
    # 检查特定字段
    assert field_name in data, f"Missing field: {field_name}"
    assert data[field_name] is not None
    
    return True
```

**测试用例：**
```yaml
script:
  # \content 转义为字符串 "content"
  - ${check_data_not_null(content.data.linesCollectList.data, 2, lines, \content)}
```

## 全局变量 vs 自定义变量

### 全局变量

**定义**：由 ApiMeter 自动注入的响应变量  
**使用**：直接使用，无需前缀

```yaml
script:
  # 全局变量（无需 $ 前缀）
  - assert status_code == 200
  - assert content.success is True
  - assert headers["Content-Type"] == "application/json"
```

### 自定义变量

**定义**：在测试用例中定义或提取的变量  
**使用**：需要 `$` 前缀或引号

```yaml
variables:
  expected_status: 200
  expected_token_length: 16

extract:
  - token: content.token
  - user_id: content.user.id

script:
  # ❌ 错误：自定义变量不能直接使用
  - assert token == "xxx"              # NameError
  
  # ✅ 正确：需要引号和 $ 前缀
  - assert "$token" is not None
  - assert len("$token") == 16
  - assert len("$token") == $expected_token_length
  
  # ✅ 正确：在函数中引用
  - ${validate_token($token)}
  - ${check_user_id($user_id)}
```

### 混合使用

```yaml
variables:
  expected_code: 0

extract:
  - token: content.token

script:
  # 全局变量
  - assert status_code == 200
  - assert content.code == $expected_code
  
  # 自定义变量（在函数中）
  - ${validate_token($token)}
  
  # 全局变量链式取值
  - assert content.user.name is not None
```

## 常见使用场景

### 场景 1：基础响应校验

```yaml
script:
  # 状态码校验
  - assert status_code == 200
  - assert ok is True
  
  # 响应头校验
  - assert headers["Content-Type"] == "application/json"
  
  # 响应体校验
  - assert content.success is True
  - assert content.code == 0
```

### 场景 2：性能监控

```yaml
script:
  # 响应时间监控
  - |
    response_time = elapsed.total_seconds
    
    # 记录慢请求
    if response_time > 1.0:
        print(f"⚠️ 慢请求警告: {url}, 耗时 {response_time}秒")
    
    # 断言最大响应时间
    assert response_time < 5.0, f"响应超时: {response_time}秒"
    
    # 不同接口不同标准
    if "/api/search" in url:
        assert response_time < 2.0, "搜索接口响应过慢"
    else:
        assert response_time < 1.0, "普通接口响应过慢"
```

### 场景 3：复杂数据校验

```yaml
script:
  # 用户数据完整性
  - assert content.user is not None
  - assert content.user.id > 0
  - assert len(content.user.name) > 0
  - assert "@" in content.user.email
  
  # 订单数据校验
  - assert len(content.orders) > 0
  - |
    for order in content.orders:
        assert order.get("id") is not None
        assert order.get("amount") > 0
        assert order.get("status") in ["pending", "paid", "completed"]
```

### 场景 4：条件校验

```yaml
script:
  # 根据用户类型校验
  - |
    if content.user.type == "vip":
        assert content.user.vip_level > 0
        assert content.user.vip_expires is not None
        assert content.user.discount >= 0.8
    elif content.user.type == "premium":
        assert content.user.premium_features is not None
        assert len(content.user.premium_features) > 0
    else:
        assert content.user.ads_enabled is True
```

### 场景 5：API 版本兼容

```yaml
script:
  # 兼容多个 API 版本
  - |
    # v1 和 v2 API 响应结构不同
    if "v1" in url:
        assert content.data.user_info is not None
        user = content.data.user_info
    elif "v2" in url:
        assert content.user is not None
        user = content.user
    else:
        raise ValueError(f"Unknown API version in URL: {url}")
    
    # 通用校验
    assert user.id > 0
    assert user.name is not None
```

## 最佳实践

### 1. 优先使用 `content`

```yaml
# ✅ 推荐：使用 content
script:
  - assert content.success is True

# ⚠️ 也可以：使用 body 或 json
script:
  - assert body.success is True
  - assert json.success is True
```

### 2. 链式取值前先检查存在性

```yaml
# ✅ 推荐：先检查再访问
script:
  - assert content.data is not None
  - assert content.data.user is not None
  - assert content.data.user.name == "Alice"

# ❌ 不推荐：直接深层访问
script:
  - assert content.data.user.name == "Alice"  # 可能 AttributeError
```

### 3. 使用有意义的错误信息

```yaml
# ✅ 推荐：提供清晰的错误信息
script:
  - assert status_code == 200, f"期望状态码200，实际: {status_code}"
  - assert content.success is True, f"API调用失败: {content.get('message', '未知错误')}"

# ❌ 不推荐：没有错误信息
script:
  - assert status_code == 200
  - assert content.success is True
```

### 4. 性能校验要合理

```yaml
# ✅ 推荐：根据接口类型设置不同标准
script:
  - |
    rt = elapsed.total_seconds
    if "/api/search" in url:
        assert rt < 2.0, f"搜索接口慢: {rt}s"
    elif "/api/report" in url:
        assert rt < 5.0, f"报表接口慢: {rt}s"
    else:
        assert rt < 1.0, f"普通接口慢: {rt}s"

# ❌ 不推荐：所有接口一刀切
script:
  - assert elapsed.total_seconds < 1.0
```

### 5. 变量转义谨慎使用

```yaml
# ✅ 只在需要时使用转义
script:
  # 正常情况：直接使用全局变量
  - assert content.success is True
  
  # 特殊情况：字段名与全局变量冲突时才转义
  - ${check_field_exists(data, \content)}

# ❌ 不要过度使用转义
script:
  - ${some_function(\status_code, \headers, \content)}  # 通常不需要
```

## 常见问题

### Q1: 为什么 `content.field` 和 `content["field"]` 都可以？

**A:** ApiMeter 使用了 `ResponseFieldProxy` 类，支持两种访问方式：

```yaml
script:
  # 点号访问（推荐，更简洁）
  - assert content.user.name == "Alice"
  
  # 字典访问（字段名包含特殊字符时使用）
  - assert content["user-name"] == "Alice"
  - assert content["content-type"] == "json"
```

### Q2: 如何访问字段名包含点号或特殊字符的字段？

**A:** 使用字典访问方式：

```yaml
script:
  # 字段名: "user.name"
  - assert content["user.name"] == "Alice"
  
  # 字段名: "content-type"
  - assert headers["content-type"] == "application/json"
```

### Q3: `content`、`body`、`json` 有什么区别？

**A:** 它们在 ApiMeter 中完全等价，都指向解析后的响应体：

```yaml
script:
  # 三者完全等价
  - assert content.success is True
  - assert body.success is True
  - assert json.success is True
```

**建议**：统一使用 `content`，保持代码风格一致。

### Q4: 如何处理响应不是 JSON 格式的情况？

**A:** 使用 `text` 变量：

```yaml
script:
  # HTML 响应
  - assert "<html" in text
  - assert "</body>" in text
  
  # XML 响应
  - assert "<?xml" in text
  
  # 纯文本响应
  - assert len(text) > 0
  - assert "success" in text.lower()
```

### Q5: 全局变量在 `validate` 中可以使用吗？

**A:** 不可以。全局变量只能在 `script` 中使用：

```yaml
# ❌ validate 中不支持
validate:
  - eq: [content.success, true]      # 会被当作字符串

# ✅ script 中支持
script:
  - assert content.success is True
```

### Q6: 如何在自定义函数中使用全局变量？

**A:** 作为参数传递：

```python
# debugtalk.py
def my_function(status, content_data):
    assert status == 200
    assert content_data.success is True
```

```yaml
script:
  # 传递全局变量作为参数
  - ${my_function(status_code, content)}
```

## 📝 总结

ApiMeter 的全局变量系统让响应数据访问变得简单直观：

| 变量 | 类型 | 最常用场景 |
|-----|------|----------|
| `status_code` | int | 状态码校验 |
| `content` | dict-like | 响应体数据校验（最常用）|
| `headers` | dict-like | 响应头校验 |
| `cookies` | dict-like | Cookie 校验 |
| `elapsed` | timedelta | 性能监控 |
| `ok` | bool | 请求成功判断 |
| `url` | str | URL 校验 |

**核心优势：**
- ✅ 直接使用，无需前缀
- ✅ 支持链式取值
- ✅ 支持变量转义
- ✅ 类型安全的代理访问

**下一步学习：**
- [自定义脚本校验详解](../prepare/script.md)
- [自定义函数高级用法](advanced-functions.md)
- [高级用法示例](../examples/advanced-examples.md)

---

**有问题？** 查看 [FAQ](../FAQ.md) 或 [提交 Issue](https://git.umlife.net/utils/apimeter/issues)

