# ApiMeter 新特性总览

欢迎来到 ApiMeter 新特性专题！本文档将帮助你快速了解 ApiMeter 相比 HttpRunner 2.x 新增的所有强大功能。

## 🎯 核心优势概览

ApiMeter 基于 HttpRunner 2.5.9 深度扩展，保留了 HttpRunner 的所有优秀特性，同时新增了多项强大功能，让 API 自动化测试更加灵活、高效、易用。

### 💡 设计理念

1. **降低学习成本** - 使用标准 Python 语法，符合开发者直觉
2. **提升表达能力** - 支持任意复杂的测试逻辑
3. **优化用户体验** - 更友好的报告展示和错误提示
4. **保持向后兼容** - 不影响现有 HttpRunner 用例

## 🚀 特性分类导航

### 📋 一、校验能力增强

#### ⭐ **1. script 自定义脚本校验** 

**重要程度**：⭐⭐⭐⭐⭐  
**版本**：v2.10.0+

这是 ApiMeter 最核心的新特性！支持使用 Python 脚本进行灵活的响应校验。

**核心优势：**
- ✅ 使用标准 Python 语法（assert、if/else、for 循环等）
- ✅ 零学习成本，符合开发者直觉
- ✅ 支持任意复杂的校验逻辑
- ✅ 逐条执行，单条失败不中断其他校验
- ✅ 详细的错误信息和执行结果

**快速示例：**
```yaml
script:
  # 基础断言
  - assert status_code == 200
  - assert content.success is True
  
  # 复杂条件
  - |
    if content.user.type == "vip":
        assert content.user.vip_level > 0
    else:
        assert content.user.ads_enabled is True
  
  # 循环校验
  - |
    for item in content.items:
        assert item.get("id") is not None
  
  # 自定义函数
  - ${validate_user_data(content.user)}
```

**📖 详细文档**：[自定义脚本校验详解](../prepare/script.md)

---

#### ⭐ **2. 全局变量无缝访问**

**重要程度**：⭐⭐⭐⭐⭐  
**版本**：v2.10.0+

在 `script` 中可以直接访问所有响应字段，无需特殊语法。

**可用的全局变量：**

| 变量名 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| `status_code` | int | HTTP状态码 | `assert status_code == 200` |
| `headers` | dict-like | 响应头 | `assert headers["Content-Type"] == "application/json"` |
| `cookies` | dict-like | Cookie信息 | `assert "session_id" in cookies` |
| `content` | dict-like | 响应内容（JSON） | `assert content.user.name is not None` |
| `body` | dict-like | 原始响应体 | `assert "success" in body` |
| `json` | dict-like | JSON响应 | `assert json.code == 0` |
| `elapsed` | object | 响应时间 | `assert elapsed.total_seconds < 2.0` |
| `ok` | bool | 请求是否成功 | `assert ok is True` |
| `reason` | str | 状态说明 | `assert reason == "OK"` |
| `url` | str | 请求URL | `assert "api" in url` |

**核心特性：**
- ✅ **链式取值**：`content.user.profile.age`
- ✅ **数组访问**：`content.items[0].price`
- ✅ **变量转义**：`\content` 转义为字符串 "content"

**📖 详细文档**：[全局变量完整指南](global-variables.md)

---

### 🔧 二、自定义函数增强

#### ⭐ **3. 列表参数支持**

**重要程度**：⭐⭐⭐⭐  
**版本**：v2.8.0+

支持向自定义函数传递列表参数。

**示例：**
```yaml
request:
  json:
    # 传递列表参数生成签名
    sign: ${get_sign_v2([$device_sn, $os_platform, $app_version])}
```

```python
# debugtalk.py
def get_sign_v2(args_list):
    content = "".join(args_list).encode("ascii")
    sign_key = SECRET_KEY.encode("ascii")
    return hmac.new(sign_key, content, hashlib.sha1).hexdigest()
```

---

#### ⭐ **4. 字典参数支持**

**重要程度**：⭐⭐⭐⭐  
**版本**：v2.8.0+

支持向自定义函数传递字典对象参数。

**示例：**
```yaml
request:
  json:
    # 传递字典参数
    sign: "${get_sign_v3({device_sn: $device_sn, os_platform: $os_platform, app_version: $app_version})}"
```

```python
# debugtalk.py
def get_sign_v3(args_dict):
    content = "".join([
        args_dict["device_sn"],
        args_dict["os_platform"],
        args_dict["app_version"]
    ]).encode("ascii")
    sign_key = SECRET_KEY.encode("ascii")
    return hmac.new(sign_key, content, hashlib.sha1).hexdigest()
```

---

#### ⭐ **5. 复杂嵌套对象参数**

**重要程度**：⭐⭐⭐⭐  
**版本**：v2.8.4+

支持传递复杂的嵌套对象配置。

**示例：**
```yaml
script:
  - "${check_nested_list_fields(content, {
      list_path: productList,
      nested_list_field: sku,
      check_fields: [id, amount, origin_amount, currency]
    })}"
```

---

#### ⭐ **6. 链式参数 | 通配符 | 正则表达式**

**重要程度**：⭐⭐⭐⭐⭐  
**版本**：v2.8.4+

支持使用通配符批量校验、正则表达式匹配、类型校验等高级功能。

**示例：**
```yaml
script:
  # 通配符批量校验（* 匹配任意层级）
  - ${check(content, 
      data.product.purchasePlan.*.sku.*.id,
      data.product.purchasePlan.*.sku.*.amount,
      data.product.purchasePlan.*.sku.*.currency
    )}
  
  # 正则表达式和类型校验
  - ${check(content,
      '_url ~= ^https?://[^\s/$.?#].[^\s]*$',  # 正则匹配
      'default_currency =* [USD, CNY]',         # 包含校验
      'default_sku @= dict',                     # 类型校验
      'product @= dict'
    )}
```

**📖 详细文档**：[自定义函数高级用法](advanced-functions.md)

---

### 📊 三、测试报告增强

#### ⭐ **7. 智能内容折叠**

**重要程度**：⭐⭐⭐⭐  
**版本**：v2.11.0+

**特性：**
- ✅ 超过 15 行的内容自动折叠
- ✅ 一键展开/折叠按钮
- ✅ 一键复制按钮
- ✅ 大幅提升报告可读性

**应用场景：**
- 长 JSON 响应
- 复杂请求体
- 详细错误信息

---

#### ⭐ **8. JSON 树形展示**

**重要程度**：⭐⭐⭐⭐⭐  
**版本**：v2.11.0+

**特性：**
- ✅ 自动识别 JSON 和 Python 字典
- ✅ 彩色语法高亮
- ✅ 节点级别展开/折叠
- ✅ 支持大型 JSON 数据（懒加载）

**应用范围：**
- Request body（请求体）
- Response body（响应体）
- Request headers（请求头）
- Response headers（响应头）
- Validator expect/actual value（校验器期望值/实际值）
- Script（自定义脚本）
- Output（脚本执行结果）

---

#### ⭐ **9. Script 执行结果展示**

**重要程度**：⭐⭐⭐⭐⭐  
**版本**：v2.11.0+

**特性：**
- ✅ 显示每条脚本的执行状态（✓ 成功 / ✗ 失败）
- ✅ 显示脚本返回值和输出
- ✅ 详细的错误堆栈信息
- ✅ 支持树形展示复杂输出

**📖 详细文档**：[测试报告增强特性](report-enhancements.md)

---

#### ⭐ **10. 报告优化选项**

**重要程度**：⭐⭐⭐  
**版本**：v2.11.1+

**特性：**
```bash
# 默认跳过成功用例（减小报告体积）
hrun testcases/ --html report.html

# 显示所有用例（包括成功的）
hrun testcases/ --html report.html --no-skip-success
```

**优势：**
- ✅ 默认 `--skip-success=True`，聚焦失败用例
- ✅ 大幅减小报告体积（可减少 50%+ 体积）
- ✅ 提升报告加载速度
- ✅ 向后兼容，可选择显示所有用例

---

### 🔐 四、其他增强特性

#### ⭐ **11. 变量转义功能**

**重要程度**：⭐⭐⭐  
**版本**：v2.9.2+

当数据字段名与全局变量同名时，使用反斜杠 `\` 转义。

**问题场景：**
```python
# 假设响应数据结构
{
    "data": {
        "content": "some value"  # 字段名为 "content"
    }
}
```

**解决方案：**
```yaml
script:
  # content 是全局变量（整个响应体）
  # 如果想表示字符串 "content"（字段名），需要转义
  - ${check_field_exists(data, \content)}
```

```python
def check_field_exists(data, field_name):
    # field_name 接收到的是字符串 "content"
    return field_name in data
```

**支持转义的全局变量：**
`\content`, `\body`, `\text`, `\json`, `\status_code`, `\headers`, `\cookies`, `\encoding`, `\ok`, `\reason`, `\url`

---

#### ⭐ **12. 自定义函数参数支持全局变量**

**重要程度**：⭐⭐⭐⭐  
**版本**：v2.8.0+

自定义函数参数可以引用全局变量和支持链式取值。

**示例：**
```yaml
validate:
  # 引用全局变量
  - eq: ["${validate_token_v2(content)}", true]
  
  # 链式取值
  - eq: ["${validate_token(content.token)}", true]
  
  # 引用自定义变量链式取值
  - eq: ["${validate_token($resp.token)}", true]
```

---

## 📊 特性成熟度评估

| 特性 | 稳定性 | 推荐度 | 文档完整度 | 适用场景 |
|-----|-------|-------|-----------|---------|
| script 自定义脚本校验 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 所有项目 |
| 全局变量无缝访问 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 所有项目 |
| 列表/字典参数 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 复杂签名场景 |
| 复杂嵌套对象 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 批量校验场景 |
| 通配符+正则 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 复杂数据结构 |
| 智能折叠 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 大数据量场景 |
| JSON树形展示 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 所有项目 |
| 变量转义 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | 特定字段名场景 |

## 🎯 快速选择指南

### 根据你的需求选择功能

**我想...**

- ✅ **编写复杂的校验逻辑** → [script 自定义脚本校验](../prepare/script.md)
- ✅ **传递复杂参数给函数** → [自定义函数高级用法](advanced-functions.md)
- ✅ **批量校验嵌套数据** → [通配符和正则表达式](advanced-functions.md#通配符批量校验)
- ✅ **优化测试报告可读性** → [测试报告增强](report-enhancements.md)
- ✅ **从 HttpRunner 迁移** → [迁移指南](migration-guide.md)
- ✅ **查看完整实战案例** → [高级用法示例](../examples/advanced-examples.md)

### 根据项目类型选择

**小型项目**（< 50 个用例）：
- ✅ script 自定义脚本校验
- ✅ 全局变量直接访问
- ✅ 基础报告功能

**中型项目**（50-200 个用例）：
- ✅ 上述所有功能
- ✅ 列表/字典参数传递
- ✅ 用例分层组织
- ✅ 参数化数据驱动

**大型项目**（200+ 个用例）：
- ✅ 上述所有功能
- ✅ 复杂嵌套对象参数
- ✅ 通配符批量校验
- ✅ 智能折叠 + 树形展示
- ✅ 报告优化选项

## 🔄 版本演进历史

### v2.12.x（最新）
- ✅ 支持报告模板折叠内容一键展开
- ✅ 优化报告模板性能（点击触发 + 懒加载）
- ✅ 修复 Python 字典数据识别问题

### v2.11.x
- ✅ 调整 skip-success 默认值为 True
- ✅ 报告模板增加 script 校验展示
- ✅ 报告模板增加内容折叠和 JSON 树形展示

### v2.10.x
- ✅ **script 自定义脚本校验功能**（核心特性）
- ✅ ResponseFieldProxy 支持点号访问
- ✅ 支持 elapsed 全局变量解析
- ✅ 变量转义功能

### v2.9.x
- ✅ 优化变量解析机制
- ✅ 修复循环依赖问题

### v2.8.x
- ✅ 自定义函数支持列表参数
- ✅ 自定义函数支持字典对象参数
- ✅ 自定义函数支持复杂嵌套对象
- ✅ 增强参数解析，支持链式取值

**📖 完整更新记录**：[CHANGELOG](../CHANGELOG.md)

## 🎓 学习路径推荐

### 新手路径（0-1 周）
1. ✅ [10分钟快速上手](../quickstart.md) - 快速体验
2. ✅ [安装说明](../Installation.md) - 环境搭建
3. ✅ [script 自定义脚本校验](../prepare/script.md) - 核心功能
4. ✅ 开始编写自己的测试用例

### 进阶路径（1-4 周）
1. ✅ [全局变量完整指南](global-variables.md) - 深入理解
2. ✅ [自定义函数高级用法](advanced-functions.md) - 复杂场景
3. ✅ [参数化数据驱动](../prepare/parameters.md) - 数据驱动
4. ✅ [测试用例分层](../prepare/testcase-layer.md) - 项目组织
5. ✅ [高级用法示例](../examples/advanced-examples.md) - 实战案例

### 专家路径（1 个月+）
1. ✅ [测试报告增强](report-enhancements.md) - 优化报告
2. ✅ [性能测试](../run-tests/load-test.md) - Locust 集成
3. ✅ [代码框架](../development/architecture.md) - 架构理解
4. ✅ [二次开发](../development/dev-api.md) - 定制开发

## 🤝 参与贡献

如果你有好的想法或发现了问题，欢迎：

- 📝 提交 Issue：[问题反馈](https://git.umlife.net/utils/apimeter/issues)
- 🔧 提交 PR：[贡献代码](https://git.umlife.net/utils/apimeter/pulls)
- 💬 技术交流：查看 [赞助与支持](../sponsors.md)

## 📚 延伸阅读

- [HttpRunner 官方文档](https://docs.httprunner.org/)
- [Python Requests 文档](https://requests.readthedocs.io/)
- [Locust 文档](https://docs.locust.io/)
- [YAML 语法教程](../prepare/yaml-issue.md)

---

**🎉 感谢使用 ApiMeter！如有任何问题，欢迎随时反馈。**

**🚀 现在就开始体验新特性吧！** → [10分钟快速上手](../quickstart.md)

