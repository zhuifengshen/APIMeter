# 快速上手指南

欢迎使用 ApiMeter！这份指南将在 **10 分钟内**帮你掌握 ApiMeter 的核心功能，轻松上手 API 自动化测试。

## 🎯 学习目标

通过本指南，你将学会：
- ✅ 安装和配置 ApiMeter
- ✅ 编写第一个测试用例
- ✅ 使用 ApiMeter 的核心特性（script 校验、全局变量、自定义函数）
- ✅ 运行测试并查看报告

## 📦 第一步：安装 ApiMeter

### 安装命令

```bash
pip install apimeter
```

### 验证安装

```bash
# 查看版本
apimeter -V

# 查看帮助
apimeter -h
```


## 🚀 第二步：准备测试环境

我们将使用 ApiMeter 自带的测试服务器进行演示。

### 启动测试服务器

首先，下载测试服务器文件：

```bash
# 方式1：如果你已经克隆了 ApiMeter 仓库
cd /path/to/apimeter
python tests/api_server.py

# 方式2：直接使用在线服务（跳过本地服务器）
# 我们后面的示例也可以使用 https://httpbin.org
```

服务器启动后，你会看到：

```
* Running on http://127.0.0.1:5000/
```

### 测试服务器接口说明

我们的测试服务器提供了一个简单的用户管理 API：

| 接口 | 方法 | 说明 |
|-----|------|------|
| `/api/get-token` | POST | 获取访问令牌 |
| `/api/users/<id>` | POST | 创建用户 |
| `/api/users/<id>` | GET | 查询用户 |
| `/api/users/<id>` | PUT | 更新用户 |
| `/api/users/<id>` | DELETE | 删除用户 |

## 📝 第三步：创建你的第一个测试用例

### 1. 创建项目结构

```bash
# 创建项目目录
mkdir my_api_test
cd my_api_test

# 创建必要的目录
mkdir -p testcases
mkdir -p api
```

### 2. 创建自定义函数文件

创建 `debugtalk.py`（放在项目根目录）：

```python
import hashlib
import hmac

SECRET_KEY = "DebugTalk"

def get_sign(*args):
    """生成签名"""
    content = "".join(args).encode("ascii")
    sign_key = SECRET_KEY.encode("ascii")
    sign = hmac.new(sign_key, content, hashlib.sha1).hexdigest()
    return sign

def validate_token_length(token):
    """校验 token 长度"""
    assert len(token) == 16, f"Token length should be 16, got {len(token)}"
    return True

def validate_user_data(user_data):
    """校验用户数据完整性"""
    required_fields = ["name", "password"]
    for field in required_fields:
        assert field in user_data, f"Missing required field: {field}"
    return True
```

### 3. 创建第一个测试用例

创建 `testcases/test_user_management.yml`：

```yaml
config:
  name: "用户管理接口测试"
  variables:
    base_url: "http://127.0.0.1:5000"
    user_agent: "iOS/10.3"
    device_sn: "TEST_DEVICE_001"
    os_platform: "ios"
    app_version: "2.8.6"

teststeps:
# ==================== 步骤1：获取访问令牌 ====================
- name: 获取访问令牌
  request:
    url: $base_url/api/get-token
    method: POST
    headers:
      Content-Type: "application/json"
      user_agent: $user_agent
      device_sn: $device_sn
      os_platform: $os_platform
      app_version: $app_version
    json:
      sign: ${get_sign($device_sn, $os_platform, $app_version)}
  
  extract:
    # 提取 token 供后续步骤使用
    - token: content.token
  
  validate:
    # 传统校验方式
    - eq: ["status_code", 200]
    - eq: ["content.success", true]
    - len_eq: ["content.token", 16]
  
  script:
    # 🆕 ApiMeter 新特性：script 自定义脚本校验
    # 支持任意 Python 脚本，更灵活强大
    
    # 基础断言
    - assert status_code == 200
    - assert content.success is True
    
    # 全局变量直接访问（无需 $ 前缀）
    - assert len(content.token) == 16
    - assert content.token is not None
    
    # 调用自定义函数
    - ${validate_token_length(content.token)}
    
    # 复杂条件判断
    - |
      if status_code == 200:
          assert content.success is True
          assert "token" in content
      else:
          assert content.success is False
    
    # 性能校验
    - assert elapsed.total_seconds < 2.0

# ==================== 步骤2：创建用户 ====================
- name: 创建新用户
  request:
    url: $base_url/api/users/1001
    method: POST
    headers:
      Content-Type: "application/json"
      device_sn: $device_sn
      token: $token  # 使用上一步提取的 token
    json:
      name: "测试用户"
      password: "123456"
  
  script:
    # 状态码校验
    - assert status_code == 201
    - assert content.success is True
    - assert content.msg == "user created successfully."
    
    # 自定义错误信息
    - assert status_code == 201, f"期望状态码 201，实际得到 {status_code}"

# ==================== 步骤3：查询用户 ====================
- name: 查询用户信息
  request:
    url: $base_url/api/users/1001
    method: GET
    headers:
      Content-Type: "application/json"
      device_sn: $device_sn
      token: $token
  
  extract:
    - user_name: content.data.name
    - user_password: content.data.password
  
  script:
    # 基础校验
    - assert status_code == 200
    - assert content.success is True
    
    # 🆕 链式取值（深层数据访问）
    - assert content.data.name == "测试用户"
    - assert content.data.password == "123456"
    
    # 🆕 调用自定义函数校验数据结构
    - ${validate_user_data(content.data)}
    
    # 数据类型校验
    - assert isinstance(content.data, dict)
    - assert len(content.data) >= 2

# ==================== 步骤4：更新用户 ====================
- name: 更新用户信息
  request:
    url: $base_url/api/users/1001
    method: PUT
    headers:
      Content-Type: "application/json"
      device_sn: $device_sn
      token: $token
    json:
      name: "更新后的用户名"
      password: "new_password"
  
  script:
    - assert status_code == 200
    - assert content.success is True
    - assert content.data.name == "更新后的用户名"
    - assert content.data.password == "new_password"

# ==================== 步骤5：删除用户 ====================
- name: 删除用户
  request:
    url: $base_url/api/users/1001
    method: DELETE
    headers:
      Content-Type: "application/json"
      device_sn: $device_sn
      token: $token
  
  script:
    - assert status_code == 200
    - assert content.success is True
    - assert content.data.name == "更新后的用户名"
```

## 🎮 第四步：运行测试

### 基础运行

```bash
# 运行单个测试文件
hrun testcases/test_user_management.yml

# 运行整个目录
hrun testcases/

# 详细模式（显示更多日志）
hrun testcases/test_user_management.yml --log-level debug
```

### 生成 HTML 报告

```bash
# 生成完整报告
hrun testcases/test_user_management.yml --html report.html

# 报告中跳过成功用例（仅显示失败和错误）
hrun testcases/test_user_management.yml --html report.html --skip-success

# 在浏览器中打开报告
open report.html  # macOS
# 或
xdg-open report.html  # Linux
# 或直接用浏览器打开 report.html
```

### 预期输出

```
test_user_management.yml
  获取访问令牌 ✓
  创建新用户 ✓
  查询用户信息 ✓
  更新用户信息 ✓
  删除用户 ✓

----------------------------------------------------------------------
Ran 5 tests in 0.123s

OK
```

## 🎯 第五步：体验 ApiMeter 核心特性

### 特性 1：script 自定义脚本校验

**传统方式** vs **ApiMeter 方式**：

```yaml
# ❌ 传统方式：validate（功能有限）
validate:
  - eq: ["status_code", 200]
  - eq: ["content.success", true]
  - len_eq: ["content.token", 16]

# ✅ ApiMeter 方式：script（功能强大）
script:
  # 直接使用 Python assert 语句
  - assert status_code == 200
  - assert content.success is True
  - assert len(content.token) == 16
  
  # 支持复杂条件
  - assert status_code in [200, 201, 202]
  
  # 支持循环
  - |
    for item in content.items:
        assert item.get("id") is not None
  
  # 支持条件判断
  - |
    if content.user.vip_level > 0:
        assert content.user.vip_expires is not None
```

### 特性 2：全局变量无缝访问

在 `script` 中，可以直接访问所有响应字段，无需特殊语法：

```yaml
script:
  # 直接访问，无需 $ 前缀
  - assert status_code == 200
  - assert headers["Content-Type"] == "application/json"
  - assert content.user.id > 0
  - assert cookies.session_id is not None
  - assert elapsed.total_seconds < 2.0
  
  # 支持链式取值（深层访问）
  - assert content.data.user.profile.age > 0
```

**可用的全局变量：**
- `status_code` - HTTP 状态码
- `headers` - 响应头
- `cookies` - Cookie 信息
- `content` / `body` / `json` - 响应体
- `elapsed` - 响应时间
- `ok` - 请求是否成功
- `reason` - 状态说明
- `url` - 请求 URL

### 特性 3：自定义函数高级参数

ApiMeter 支持向自定义函数传递复杂参数：

```yaml
# 1️⃣ 简单参数
script:
  - ${validate_token(content.token)}

# 2️⃣ 列表参数
request:
  json:
    sign: ${get_sign_v2([$device_sn, $os_platform, $app_version])}

# 3️⃣ 字典参数
request:
  json:
    sign: "${get_sign_v3({device_sn: $device_sn, platform: $os_platform})}"

# 4️⃣ 复杂嵌套对象
script:
  - "${check_nested_fields(content, {list_path: productList, check_fields: [id, name, price]})}"
```

对应的 `debugtalk.py` 函数：

```python
# 1️⃣ 简单参数
def validate_token(token):
    assert len(token) == 16
    return True

# 2️⃣ 列表参数
def get_sign_v2(args_list):
    content = "".join(args_list).encode("ascii")
    sign_key = SECRET_KEY.encode("ascii")
    return hmac.new(sign_key, content, hashlib.sha1).hexdigest()

# 3️⃣ 字典参数
def get_sign_v3(args_dict):
    content = "".join([args_dict["device_sn"], args_dict["platform"]]).encode("ascii")
    sign_key = SECRET_KEY.encode("ascii")
    return hmac.new(sign_key, content, hashlib.sha1).hexdigest()

# 4️⃣ 复杂嵌套对象
def check_nested_fields(data, config):
    list_path = config["list_path"]
    check_fields = config["check_fields"]
    for item in data[list_path]:
        for field in check_fields:
            assert field in item
    return True
```

### 特性 4：变量转义

当数据字段名与全局变量同名时，使用反斜杠转义：

```yaml
script:
  # content 是全局变量（响应内容）
  # \content 是字符串 "content"（字段名）
  - ${check_field_exists(data, \content)}
```

```python
def check_field_exists(data, field_name):
    """
    检查数据中是否存在指定字段
    field_name 接收到的是字符串 "content"
    """
    return field_name in data
```

## 📊 第六步：查看测试报告

运行测试后生成的 HTML 报告包含：

### 1. 测试概览
- ✅ 总用例数、成功数、失败数
- ✅ 执行时间统计
- ✅ 成功率百分比

### 2. 详细结果（🆕 ApiMeter 增强特性）

**智能折叠**：
- 超过 15 行的内容自动折叠
- 点击展开/折叠
- 一键复制按钮

**JSON 树形展示**：
- 自动识别 JSON 和 Python 字典
- 彩色语法高亮
- 节点级别展开/折叠
- 提升大数据量场景的可读性

**Script 校验展示**：
- 每条脚本的执行结果
- 失败脚本的详细错误信息
- 执行输出和返回值

## 🎓 进阶学习

### 参数化测试

创建数据文件 `data/users.csv`：

```csv
user_id,user_name,password
1001,Alice,pass123
1002,Bob,pass456
1003,Charlie,pass789
```

在测试用例中使用：

```yaml
config:
  name: "参数化用户创建测试"
  parameters:
    - user_id-user_name-password: ${P(data/users.csv)}

teststeps:
- name: "创建用户 - ${user_name}"
  request:
    url: $base_url/api/users/$user_id
    method: POST
    json:
      name: $user_name
      password: $password
  script:
    - assert status_code == 201
    - assert content.success is True
```

### 测试用例分层

将接口定义和测试逻辑分离：

**api/create_user.yml**（接口定义）：

```yaml
name: 创建用户接口
variables:
  user_id: 9999
  user_name: "default"
  user_password: "000000"
request:
  url: $base_url/api/users/$user_id
  method: POST
  headers:
    Content-Type: "application/json"
    device_sn: $device_sn
    token: $token
  json:
    name: $user_name
    password: $user_password
validate:
  - eq: ["status_code", 201]
```

**testcases/test_create_user.yml**（测试用例）：

```yaml
config:
  name: "创建用户测试场景"
  variables:
    base_url: "http://127.0.0.1:5000"

teststeps:
- name: 获取 token
  testcase: testcases/setup.yml
  extract:
    - token

- name: 创建用户 Alice
  api: api/create_user.yml
  variables:
    user_id: 2001
    user_name: "Alice"
    user_password: "alice123"
  script:
    - assert content.success is True

- name: 创建用户 Bob
  api: api/create_user.yml
  variables:
    user_id: 2002
    user_name: "Bob"
    user_password: "bob456"
  script:
    - assert content.success is True
```

### 环境变量管理

创建 `.env` 文件：

```bash
# 开发环境
BASE_URL=http://127.0.0.1:5000
DEVICE_SN=DEV_DEVICE_001

# 测试环境
# BASE_URL=https://test.example.com
# DEVICE_SN=TEST_DEVICE_001

# 生产环境
# BASE_URL=https://api.example.com
# DEVICE_SN=PROD_DEVICE_001
```

在测试用例中使用：

```yaml
config:
  name: "环境配置示例"
  variables:
    base_url: ${ENV(BASE_URL)}
    device_sn: ${ENV(DEVICE_SN)}
```

## 🔥 实战练习

### 练习 1：HTTP 接口测试

使用公共测试接口 https://httpbin.org 练习：

```yaml
config:
  name: "HTTPBin 测试练习"
  base_url: "https://httpbin.org"

teststeps:
- name: GET 请求测试
  request:
    url: /get
    method: GET
    params:
      name: "ApiMeter"
      version: "2.12"
  script:
    - assert status_code == 200
    - assert json.args.name == "ApiMeter"
    - assert json.args.version == "2.12"
    - assert json.url.startswith("https://httpbin.org")

- name: POST 请求测试
  request:
    url: /post
    method: POST
    json:
      username: "test_user"
      email: "test@example.com"
  script:
    - assert status_code == 200
    - assert json.json.username == "test_user"
    - assert json.json.email == "test@example.com"

- name: 响应头测试
  request:
    url: /headers
    method: GET
  script:
    - assert status_code == 200
    - assert "User-Agent" in json.headers
    - assert json.headers["Host"] == "httpbin.org"

- name: 响应状态码测试
  request:
    url: /status/404
    method: GET
  script:
    - assert status_code == 404
    - assert ok is False
```

### 练习 2：认证流程测试

模拟完整的 OAuth2 认证流程：

```yaml
config:
  name: "OAuth2 认证流程"
  variables:
    client_id: "test_client"
    client_secret: "test_secret"

teststeps:
- name: 获取授权码
  request:
    url: https://oauth.example.com/authorize
    method: POST
    json:
      client_id: $client_id
      response_type: "code"
  extract:
    - auth_code: content.code
  script:
    - assert status_code == 200
    - assert content.code is not None

- name: 获取访问令牌
  request:
    url: https://oauth.example.com/token
    method: POST
    json:
      client_id: $client_id
      client_secret: $client_secret
      code: $auth_code
      grant_type: "authorization_code"
  extract:
    - access_token: content.access_token
    - refresh_token: content.refresh_token
  script:
    - assert status_code == 200
    - assert content.access_token is not None
    - assert content.token_type == "Bearer"
    - assert content.expires_in > 0

- name: 使用访问令牌请求 API
  request:
    url: https://api.example.com/user/profile
    method: GET
    headers:
      Authorization: "Bearer $access_token"
  script:
    - assert status_code == 200
    - assert content.user_id is not None
```

## 📚 下一步学习

恭喜你！你已经掌握了 ApiMeter 的核心功能。接下来可以：

### 深入学习
- 📖 [自定义脚本校验详解](prepare/script.md) - 掌握 script 的所有用法
- 📖 [自定义函数高级用法](features/advanced-functions.md) - 学习复杂参数传递
- 📖 [全局变量完整指南](features/global-variables.md) - 了解所有可用变量
- 📖 [测试报告增强](features/report-enhancements.md) - 了解报告优化特性

### 实战案例
- 🎯 [高级用法示例](examples/advanced-examples.md) - 真实场景案例
- 🎯 [完整项目示例](examples/demo-klook/README.md) - 企业级项目结构

### 进阶主题
- 🚀 [性能测试](run-tests/load-test.md) - 使用 Locust 进行压测
- 🚀 [持续集成](run-tests/cli.md) - 集成到 CI/CD 流程
- 🚀 [用例分层](prepare/testcase-layer.md) - 优化用例组织结构

## ❓ 常见问题

### 1. 为什么推荐使用 script 而不是 validate？

**回答**：

- ✅ **script 优势**：
  - 使用标准 Python 语法，零学习成本
  - 支持任意复杂逻辑（条件、循环、函数）
  - 逐条执行，单条失败不影响其他校验
  - 错误信息更清晰
  
- ⚠️ **validate 局限**：
  - 需要记忆特定语法
  - 复杂逻辑难以实现
  - 功能相对固定

**建议**：新项目优先使用 `script`，两者可以共存。

### 2. script 中的变量需要加 $ 前缀吗？

**回答**：

```yaml
script:
  # ❌ 错误：不需要 $ 前缀
  - assert $status_code == 200
  
  # ✅ 正确：全局变量直接使用
  - assert status_code == 200
  - assert content.token is not None
  
  # ✅ 正确：自定义变量需要引号和 $
  - assert "$token" is not None
  - assert len("$token") == 16
  
  # ✅ 正确：在函数中引用自定义变量
  - ${validate_token($token)}
```

### 3. 如何调试失败的测试？

**方法 1**：查看详细日志

```bash
hrun testcases/test.yml --log-level debug
```

**方法 2**：在 debugtalk.py 中添加日志

```python
from apimeter.logger import log_debug, log_info

def my_function(data):
    log_debug(f"接收到的数据: {data}")
    # 你的逻辑
    result = process(data)
    log_info(f"处理结果: {result}")
    return result
```

**方法 3**：查看 HTML 报告

报告中包含每个步骤的完整请求和响应信息，以及 script 执行详情。

### 4. 如何组织大型测试项目？

**推荐结构**：

```
my_project/
├── api/                    # 接口定义层
│   ├── auth/
│   │   ├── login.yml
│   │   └── logout.yml
│   └── user/
│       ├── create.yml
│       ├── update.yml
│       └── delete.yml
├── testcases/             # 测试用例层
│   ├── test_auth.yml
│   └── test_user_crud.yml
├── testsuites/            # 测试套件层
│   └── full_regression.yml
├── data/                  # 测试数据
│   ├── users.csv
│   └── products.csv
├── debugtalk.py           # 自定义函数
├── .env                   # 环境配置
└── reports/               # 测试报告
```

## 🎉 总结

你已经学会了：

- ✅ 安装和运行 ApiMeter
- ✅ 编写基本测试用例（request + validate + script）
- ✅ 使用 script 进行强大的自定义校验
- ✅ 使用全局变量和链式取值
- ✅ 编写和调用自定义函数
- ✅ 生成和查看 HTML 报告
- ✅ 参数化测试和用例分层

**ApiMeter 的核心优势**：

| 特性 | 传统工具 | ApiMeter |
|-----|---------|----------|
| 校验能力 | 固定语法 | Python 脚本，无限可能 |
| 学习成本 | 需记忆特定语法 | 标准 Python，零学习成本 |
| 复杂逻辑 | 有限支持 | 完全支持（条件、循环、函数）|
| 错误处理 | 单点失败 | 逐条执行，容错处理 |
| 测试报告 | 基础展示 | 智能折叠、树形展示 |

现在，开始你的 API 自动化测试之旅吧！🚀

---

**需要帮助？**
- 📖 [完整文档](https://zhuifengshen.github.io/APIMeter/)
- 🐛 [问题反馈](https://git.umlife.net/utils/apimeter/issues)
- 💬 [技术交流群](sponsors.md)

