# api_server.py 接口文档

## 一、概述

api_server.py，是一个 Resful 风格的简易 API 服务，提供了对用户账号进行增删改查（CRUD）功能的接口服务，包含了接口的签名校验机制，方便 API 自动化测试工具的开发与调试！

## 二、启动服务

```
# 命令行启动（默认5000端口）
python api_server.py
```


## 二、接口文档

### 1. API V1 接口说明

- 接口基准地址：http://127.0.0.1:5000/
- 使用 HTTP Status Code 标识状态
- 数据返回格式统一使用 JSON
- API V1 认证统一使用 Token 认证
- 需要授权的 API ，必须在请求头中使用`device-sn`字段提供设备序列号和 `token` 字段提供访问令牌
- 全局请求头

| 参数名       | 参数类型 | 参数说明   | 备注                        |
| ------------ | -------- | ---------- | --------------------------- |
| Content-Type | String   | 内容类型   | application/json            |
| device-sn    | String   | 设备序列号 | 唯一设备标识符              |
| token        | String   | 访问令牌   | 拥有 token 的设备才有访问权 |

#### 1.1. 支持的请求方法

- GET（SELECT）：从服务器取出资源（一项或多项）。
- POST（CREATE）：在服务器新建一个资源。
- PUT（UPDATE）：在服务器更新资源（客户端提供改变后的完整资源）。
- PATCH（UPDATE）：在服务器更新资源（客户端提供改变的属性）。
- DELETE（DELETE）：从服务器删除资源。
- HEAD：获取资源的元数据。
- OPTIONS：获取信息，关于资源的哪些属性是客户端可以改变的。

#### 1.2. 通用返回状态说明

| _状态码_ | _含义_                | _说明_                                              |
| -------- | --------------------- | --------------------------------------------------- |
| 200      | OK                    | 请求成功                                            |
| 201      | CREATED               | 创建成功                                            |
| 204      | DELETED               | 删除成功                                            |
| 400      | BAD REQUEST           | 请求的地址不存在或者包含不支持的参数                |
| 401      | UNAUTHORIZED          | 未授权                                              |
| 403      | FORBIDDEN             | 被禁止访问                                          |
| 404      | NOT FOUND             | 请求的资源不存在                                    |
| 422      | Unprocesable entity   | [POST/PUT/PATCH] 当创建一个对象时，发生一个验证错误 |
| 500      | INTERNAL SERVER ERROR | 内部错误                                            |

---

### 2. 具体接口说明

#### 2.1. 获取令牌

- 请求路径：/api/get-token
- 请求方法：post
- 请求头

| 参数名      | 参数类型 | 参数说明   | 备注 |
| ----------- | -------- | ---------- | ---- |
| User-Agent  | String   | 用户代理   |      |
| device-sn   | String   | 设备序列号 |      |
| os_platform | String   | 系统平台   |      |
| app_version | String   | 应用版本   |      |

- 请求参数

| 参数名 | 参数类型 | 参数说明 | 备注                     |
| ------ | -------- | -------- | ------------------------ |
| sign   | String   | 加密签名 | 根据请求头和密钥加密生成 |

- 响应参数

| 参数名  | 参数类型 | 参数说明 | 备注       |
| ------- | -------- | -------- | ---------- |
| success | Boolean  | 是否成功 |            |
| token   | String   | 访问令牌 | 长度 16 位 |

- 成功返回

```
状态码：200
响应体：
{
    'success': true,
    'token': "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1aW"
}
```

- 失败返回

```
状态码：403
响应体：
{
    'success': false,
    'msg': "Authorization failed!"
}
```

- 签名生成算法

```python
def get_sign(*args):
    SECRECT_KEY = 'DebugTalk'
	content = ''.join(args).encode('ascii')
	sign_key = SECRECT_KEY.encode('ascii')
	sign = hmac.new(sign_key, content, hashlib.sha1).hexdigest()
	return sign

sign = get_sign(user_agent, device_sn, os_platform, app_version)

```

#### 2.2. 新建用户

- 请求路径：/api/users/:id
- 请求方法：post
- 请求参数

| 参数名   | 参数类型 | 参数说明 | 备注 |
| -------- | -------- | -------- | ---- |
| id       | Int      | 用户 ID  |      |
| name     | String   | 用户名   |      |
| password | String   | 密码     |      |

- 响应参数

| 参数名  | 参数类型 | 参数说明 | 备注 |
| ------- | -------- | -------- | ---- |
| success | Boolean  | 是否成功 |      |
| msg     | String   | 说明信息 |      |

- 成功返回

```
状态码：201
响应体：
{
    'success': true,
    'msg': "user created successfully."
}
```

- 失败返回

```
状态码：422
响应体：
{
    'success': false,
    'msg': "user already existed."
}
```

#### 2.3. 根据 ID 查询用户信息

- 请求路径：/api/users/:id
- 请求方法：get
- 响应参数

| 参数名   | 参数类型 | 参数说明 | 备注 |
| -------- | -------- | -------- | ---- |
| success  | Boolean  | 是否成功 |      |
| name     | String   | 用户名   |      |
| password | String   | 密码     |      |

- 成功返回

```
状态码：200
响应体：
{
    'success': true,
    'data': {
        'name': 'admin',
        'password': '123456'
    }
}
```

- 失败返回

```
状态码：404
响应体：
{
    'success': fasle,
    'data': {}
}
```

#### 2.4. 更新用户信息

- 请求路径：/api/users/:id
- 请求方法：put
- 请求参数

| 参数名   | 参数类型 | 参数说明 | 备注 |
| -------- | -------- | -------- | ---- |
| id       | Int      | 用户 ID  |      |
| name     | String   | 用户名   |      |
| password | String   | 密码     |      |

- 响应参数

| 参数名  | 参数类型 | 参数说明 | 备注 |
| ------- | -------- | -------- | ---- |
| success | Boolean  | 是否成功 |      |
| data    | Dict     | 用户信息 |      |

- 成功返回

```
状态码：200
响应体：
{
    'success': true,
    'data': {
        'name': 'admin',
        'password': '123456'
    }
}
```

- 失败返回

```
状态码：404
响应体：
{
    'success': fasle,
    'data': {}
}
```

#### 2.5. 删除用户信息

- 请求路径：/api/users/:id
- 请求方法：delete
- 请求参数

| 参数名 | 参数类型 | 参数说明 | 备注 |
| ------ | -------- | -------- | ---- |
| id     | Int      | 用户 ID  |      |

- 响应参数

| 参数名  | 参数类型 | 参数说明 | 备注 |
| ------- | -------- | -------- | ---- |
| success | Boolean  | 是否成功 |      |
| data    | Dict     | 用户信息 |      |

- 成功返回

```
状态码：200
响应体：
{
    'success': true,
    'data': {
        'name': 'admin',
        'password': '123456'
    }
}
```

- 失败返回

```
状态码：404
响应体：
{
    'success': fasle,
    'data': {}
}
```

#### 2.6. 用户数据列表

- 请求路径：/api/users
- 请求方法：get
- 响应参数

| 参数名  | 参数类型 | 参数说明     | 备注 |
| ------- | -------- | ------------ | ---- |
| success | Boolean  | 是否成功     |      |
| count   | Int      | 用户总数     |      |
| items   | Array    | 用户数据集合 |      |

- 成功返回

```
状态码：200
响应体：
{
    'success': true,
    'count': 3,
    'items': [
        {'name': 'admin1', 'password': '123456'},
        {'name': 'admin2', 'password': '123456'},
        {'name': 'admin3', 'password': '123456'}
    ]
}
```

#### 2.7. 清空用户数据

- 请求路径：/api/reset-all
- 请求方法：get
- 响应参数

| 参数名  | 参数类型 | 参数说明 | 备注 |
| ------- | -------- | -------- | ---- |
| success | Boolean  | 是否成功 |      |

- 成功返回

```
状态码：200
响应体：
{
    'success': true
}
```
