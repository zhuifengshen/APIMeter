# ApiMeter

<p align="center">
  <img src="https://img.shields.io/pypi/v/apimeter.svg" alt="Version">
  <img src="https://img.shields.io/badge/python-3.6%2B-blue" alt="Python">
  <img src="https://img.shields.io/badge/license-Apache2.0-green" alt="License">
  <img src="https://img.shields.io/badge/core-简单强大轻量级-orange" alt="Core">
</p>


*ApiMeter* 是一个简洁优雅、功能强大的 HTTP(S) 接口测试框架，基于 httprunner.py 扩展，实现只需编写维护一份 `YAML/JSON` 脚本，便可高效实现接口自动化测试、性能测试、线上监控、持续集成等多种测试需求。Enjoy! ✨ 🚀 ✨


## ✨ 为什么选择 ApiMeter？

### 🔍 httprunner.py 已停止更新维护

- 2022-04-30 httprunner.py 发布 v2.5.9 后已停止更新维护；
- httprunner.py 简单强大轻量级，适合接口平台集成化开发，而 HttpRunner 已开始往大而全方向发展；
- httprunner.py 随着日常业务迭代与应用，越来越多的新需求不断产生且需要被满足，因此催生了 ApiMeter；

### 🔥 相比 httprunner.py 的核心优势

#### 1. **增加更灵活的校验能力 - script 自定义脚本校验**

**validate校验方式**需要记忆各种校验器语法，功能有限：
```yaml
validate:
  - eq: ["status_code", 200]
  - len_eq: ["content.token", 16]
  - eq: ["content.success", true]
```

**script校验方式**支持任意 Python 脚本，零学习成本：
```yaml
script:
  # 直接使用 Python assert 语句
  - assert status_code == 200
  - assert len(content.token) == 16
  - assert content.success is True
  
  # 支持复杂条件判断
  - |
    if status_code == 200:
        assert content.success is True
    else:
        assert content.error_code is not None
  
  # 支持循环校验
  - |
    for item in content.items:
        assert item.get("id") is not None

  # 性能校验
  - assert elapsed.total_seconds < 2.0

  # 调用自定义函数
  - ${validate_user_data(content.user)}
```

**核心特性：**
- ✅ 使用标准 Python 语法，符合开发者直觉
- ✅ 支持条件判断、循环、自定义函数
- ✅ 逐条执行，单条失败不中断其他校验，提供详细执行结果和错误信息
- ✅ 自定义函数校验遵循assert理念「失败即异常」，释放无限校验方式的可能性
- ✅ 非常适合批量数据校验场景，推荐结合[通用数据校验器](https://github.com/zhuifengshen/general-validator)使用

#### 2. **更强大的自定义函数参数支持**

**支持列表参数**：
```yaml
request:
  json:
    # 传递列表参数
    sign: ${get_sign_v2([$device_sn, $os_platform, $app_version])}
```

**支持字典参数**：
```yaml
request:
  json:
    # 传递字典参数
    sign: "${get_sign_v3({device_sn: $device_sn, os_platform: $os_platform, app_version: $app_version})}"
```

**支持复杂嵌套对象**：
```yaml
script:
  # 传递复杂配置对象
  - "${check_nested_list_fields(content, {list_path: productList, nested_field: sku, check_fields: [id, amount, currency]})}"
```

**支持链式参数 + 通配符 + 正则表达式**：
```yaml
script:
  # 通配符批量校验
  - ${check(content, data.product.purchasePlan.*.sku.*.id, data.product.purchasePlan.*.sku.*.amount)}
  
  # 正则表达式和类型校验
  - ${check(content, '_url ~= ^https?://[^\s/$.?#].[^\s]*$', 'default_currency =* [USD, CNY]', 'product @= dict')}
```

#### 3. **更灵活的全局变量系统**

**无缝访问响应数据**，无需特殊语法：
```yaml
script:
  # 直接访问全局变量（无需 $ 前缀）
  - assert status_code == 200
  - assert headers["Content-Type"] == "application/json"
  - assert content.user.name is not None
  - assert cookies.session_id is not None
  
  # 支持链式取值（深层数据访问）
  - assert content.data.user.profile.age > 18
  - assert content.items[0].price > 0
```

**支持变量转义**，解决字段名与全局变量冲突：
```yaml
script:
  # \content 会被解析为字符串 "content"，而不是全局变量 content
  - ${check_field_exists(data, \content)}
```

**可用的全局变量：**
`status_code`, `headers`, `cookies`, `content`, `body`, `json`, `elapsed`, `ok`, `reason`, `url`, `response`

#### 4. **更友好的测试报告**

**智能内容折叠**：
- 超过 15 行的内容自动折叠，提升可读性
- 一键展开/折叠和复制

**JSON 树形展示**：
- 自动识别 JSON 和 Python 字典
- 彩色语法高亮
- 节点级别展开/折叠
- 应用于所有关键数据字段（请求体、响应体、请求头、响应头、校验器、Script）

**Script 执行结果展示**：
- 每条脚本的执行结果
- 失败脚本的详细错误信息
- 执行结果返回值输出

**报告优化选项**：
```bash
# 报告中跳过成功用例（仅显示失败和错误，减小报告体积）
hrun testcases/ --html report.html --skip-success
```

## 🚀 快速开始

### 安装

```bash
pip install apimeter
```

安装后可用命令：`apimeter`、`meter`、`api`、`hrun`、`apilocust`

### 5 分钟快速上手

创建测试文件 `test_api.yml`：

```yaml
config:
  name: "快速开始示例"
  variables:
    base_url: "https://httpbin.org"

teststeps:
- name: GET 请求测试
  request:
    url: $base_url/get
    method: GET
    params:
      name: "ApiMeter"
  script:
    - assert status_code == 200
    - assert json.args.name == "ApiMeter"
    - assert json.url.startswith("https://httpbin.org")

- name: POST 请求测试
  request:
    url: $base_url/post
    method: POST
    json:
      username: "test_user"
      email: "test@example.com"
  script:
    - assert status_code == 200
    - assert json.json.username == "test_user"
    - |
      # 复杂校验逻辑
      if json.json.email:
          assert "@" in json.json.email
```

### 运行测试

```bash
# 基础运行
apimeter test_api.yml

# 优化报告（跳过成功用例）
apimeter test_api.yml --skip-success
```

## 📖 完整文档

### 🎓 快速学习
- **[10分钟快速上手](docs/quickstart.md)** - 零基础入门指南 ⭐
- [安装说明](docs/Installation.md) - 详细的安装和配置
- [快速上手案例](docs/examples/quickstart-case.md) - 完整项目示例

### 🆕 新特性专题
- **[新特性总览](docs/features/README.md)** - 所有新功能索引 ⭐
- **[自定义脚本校验](docs/prepare/script.md)** - script 详细用法 ⭐
- [自定义函数高级用法](docs/features/advanced-functions.md) - 复杂参数传递
- [全局变量完整指南](docs/features/global-variables.md) - 所有可用变量
- [测试报告增强](docs/features/report-enhancements.md) - 报告优化特性

### 📚 核心功能
- [项目文件组织](docs/prepare/project-structure.md) - 项目结构最佳实践
- [测试用例组织](docs/prepare/testcase-structure.md) - 用例编写规范
- [测试用例分层](docs/prepare/testcase-layer.md) - API/TestCase/TestSuite 分层
- [参数化数据驱动](docs/prepare/parameters.md) - 数据驱动测试
- [校验器用法](docs/prepare/validate.md) - 传统校验器
- [环境变量](docs/prepare/dot-env.md) - 环境配置管理
- [hook机制](docs/prepare/request-hook.md) - 请求前后处理

### 🎯 测试执行
- [运行测试(CLI)](docs/run-tests/cli.md) - 命令行使用
- [测试报告](docs/run-tests/report.md) - 报告详解
- [性能测试](docs/run-tests/load-test.md) - 基于 Locust 的压测

### 💡 高级主题
- [高级用法示例](docs/examples/advanced-examples.md) - 实战案例
- [代码框架](docs/development/architecture.md) - 架构设计
- [二次开发](docs/development/dev-api.md) - 扩展开发

### 📋 其他
- [CHANGELOG](docs/CHANGELOG.md) - 版本更新记录
- [FAQ](docs/FAQ.md) - 常见问题
- [相关资料](docs/related-docs.md) - 扩展阅读

**在线文档**：[https://zhuifengshen.github.io/APIMeter/](https://zhuifengshen.github.io/APIMeter/)

## 🔥 核心校验特性对比

| 特性 | 传统工具/HttpRunner | ApiMeter |
|-----|-------------------|----------|
| **校验能力** | 固定校验器语法 | ✅ Python 脚本，无限可能 |
| **学习成本** | 需记忆特定语法 | ✅ 标准 Python，零学习成本 |
| **复杂逻辑** | 有限支持 | ✅ 完全支持（条件、循环、函数）|
| **错误处理** | 单点失败中断 | ✅ 逐条执行，容错处理 |
| **全局变量** | 有限的变量访问 | ✅ 链式取值 + 变量转义 |
| **函数参数** | 简单参数 | ✅ 列表/字典/嵌套对象/通配符 |
| **测试报告** | 基础展示 | ✅ 智能折叠 + JSON树形展示 |
| **数据校验** | 单一固定模式 | ✅ 自定义任意校验逻辑 |
| **调试能力** | 基础日志 | ✅ 详细执行结果和错误信息 |

## 💼 使用场景

### 场景 1：复杂业务逻辑校验
```yaml
script:
  # 根据用户类型进行不同校验
  - |
    if content.user.type == "vip":
        assert content.user.vip_level > 0
        assert content.user.discount >= 0.8
    elif content.user.type == "premium":
        assert content.user.premium_expires is not None
    else:
        assert content.user.ads_enabled is True
```

### 场景 2：批量数据校验
```yaml
script:
  # 校验商品列表中的每个商品
  - |
    assert len(content.products) > 0
    for product in content.products:
        assert product.get("id") is not None
        assert product.get("price") > 0
        assert product.get("status") in ["active", "inactive"]
        if product.get("discount"):
            assert 0 < product["discount"] < 1
```

### 场景 3：复杂签名生成
```yaml
request:
  json:
    # 传递复杂参数生成签名
    sign: "${generate_signature({
      method: $method,
      url: $url,
      timestamp: $timestamp,
      nonce: $nonce,
      body: $request_body
    })}"
```

### 场景 4：性能与功能结合测试
```yaml
script:
  # 同时校验功能和性能
  - assert status_code == 200
  - assert content.success is True
  - assert elapsed.total_seconds < 1.0, f"响应时间过长: {elapsed.total_seconds}s"
  - assert len(content.items) <= 100, "返回数据量过大"
```


## 🤝 贡献与支持

### 问题反馈
如果你在使用过程中遇到问题，欢迎提交 Issue：
- [提交 Bug](https://github.com/zhuifengshen/APIMeter/issues)
- [功能建议](https://github.com/zhuifengshen/APIMeter/issues)
- 技术交流

### 贡献代码
**🧩 欢迎提交 Pull Request，让 ApiMeter 变得更好！**

**⭐ 如果 ApiMeter 对你有帮助，请给个 Star 支持一下！**

**🚀 现在就开始你的 API 自动化测试之旅吧！** → [10分钟快速上手](docs/quickstart.md)



## 🙏 致谢

ApiMeter 基于以下优秀的开源项目：
- [HttpRunner](https://github.com/httprunner/httprunner.py) - HTTP(S) 测试框架基础
- [Requests](https://requests.readthedocs.io/) - 优雅的 HTTP 库
- [Locust](https://locust.io/) - 现代化性能测试工具
- [Jinja2](https://jinja.palletsprojects.com/) - 模板引擎


## 🛡️ Copyright

Copyright (c) 2025 Devin Zhang

This software is based on [httprunner.py](https://github.com/httprunner/httprunner.py),  
which is licensed under the Apache License, Version 2.0.  
This project continues to be distributed under the same license.

You may obtain a copy of the License at:

<http://www.apache.org/licenses/LICENSE-2.0>