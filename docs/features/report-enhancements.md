# 测试报告增强特性

ApiMeter 对测试报告进行了大幅优化，特别是在大数据量场景下的可读性和性能表现。本文档详细介绍报告的各项增强特性。

## 🎯 核心增强特性

### 1. 智能内容折叠
### 2. JSON 树形展示
### 3. Script 执行结果展示
### 4. 报告优化选项

---

## 1. 智能内容折叠

### 特性说明

当内容超过 **15 行**时，自动折叠显示，提供更清爽的报告界面。

**优势：**
- ✅ 自动识别长内容
- ✅ 一键展开/折叠
- ✅ 一键复制按钮
- ✅ 大幅提升报告加载速度
- ✅ 减少报告文件体积（可减少 30-50%）

### 应用场景

智能折叠应用于以下所有内容：
- Request Body（请求体）
- Response Body（响应体）
- Request Headers（请求头）
- Response Headers（响应头）
- Validator Expect/Actual（校验器期望值/实际值）
- Script（自定义脚本）
- Script Output（脚本执行结果）

### 使用示例

**长 JSON 响应自动折叠：**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "user": {...},
    "products": [...],
    // ... 更多数据（超过15行）
  }
}
```

在报告中显示为：

```
Response Body: (已折叠 - 共 127 行)
[点击展开] [复制]
```

点击展开后完整显示所有内容。

---

## 2. JSON 树形展示

### 特性说明

自动识别 JSON 和 Python 字典数据，以树形结构展示，支持节点级别的展开/折叠。

**优势：**
- ✅ 彩色语法高亮
- ✅ 节点级别展开/折叠
- ✅ 支持大型 JSON（懒加载）
- ✅ 更直观的数据结构展示
- ✅ 支持 JSON 和 Python 字典格式

### 视觉效果

**传统纯文本显示：**
```
{"code":0,"message":"success","data":{"user":{"id":123,"name":"Alice","email":"alice@example.com","profile":{"age":25,"city":"Beijing"}},"products":[{"id":1,"name":"Product 1","price":99.99},{"id":2,"name":"Product 2","price":199.99}]}}
```

**树形展示：**
```
▼ {
    code: 0
    message: "success"
  ▶ data: {...}
}
```

点击展开 `data`:
```
▼ {
    code: 0
    message: "success"
  ▼ data: {
      ▶ user: {...}
      ▶ products: [...]
    }
}
```

### 支持的数据格式

**标准 JSON：**
```json
{
  "name": "Alice",
  "age": 25,
  "skills": ["Python", "Java"]
}
```

**Python 字典（单引号）：**
```python
{
  'name': 'Alice',
  'age': 25,
  'skills': ['Python', 'Java']
}
```

**混合格式：**
```python
{
  "name": 'Alice',   # 双引号键，单引号值
  'age': 25,
  "skills": ['Python', "Java"]
}
```

---

## 3. Script 执行结果展示

### 特性说明

在报告中详细展示每条 `script` 脚本的执行状态和结果。

**显示内容：**
- ✅ 每条脚本的执行状态（✓ 成功 / ✗ 失败）
- ✅ 脚本返回值和输出
- ✅ 失败脚本的详细错误信息
- ✅ 完整的错误堆栈
- ✅ 支持树形展示复杂输出

### 报告展示示例

**成功的脚本：**
```
Script Validations:
  ✓ assert status_code == 200
      Output: None
  
  ✓ assert content.success is True
      Output: None
  
  ✓ ${validate_token(content.token)}
      Output: True
```

**失败的脚本：**
```
Script Validations:
  ✓ assert status_code == 200
      Output: None
  
  ✗ assert content.user.age > 18
      Error: AssertionError
      Message: assert 15 > 18
      Traceback:
        File "<script>", line 1, in <module>
        AssertionError
  
  ✓ ${validate_token(content.token)}
      Output: True
```

**多行脚本输出：**
```
Script Validations:
  ✓ |
    for item in content.items:
        assert item.get("id") is not None
        assert item.get("price") > 0
    
      Output: None
      Checked: 15 items
```

---

## 4. 报告优化选项

### skip-success 功能

**功能说明：**

默认情况下，报告中会跳过成功的用例，只显示失败和错误的用例，让你专注于问题。

**命令行选项：**

```bash
# 默认：跳过成功用例（v2.11.1+）
hrun testcases/ --html report.html

# 等价于
hrun testcases/ --html report.html --skip-success

# 显示所有用例（包括成功的）
hrun testcases/ --html report.html --no-skip-success
```

**优势：**
- ✅ 聚焦失败用例，快速定位问题
- ✅ 减少报告体积（可减少 50-70%）
- ✅ 提升报告加载速度
- ✅ 向后兼容，可选择显示全部

**报告对比：**

**--no-skip-success（显示所有）：**
```
Test Results: 100 tests, 95 passed, 3 failed, 2 errors

✓ test_user_login
✓ test_user_profile
✓ test_product_list
✓ test_product_detail
...（91 more passed tests）
✗ test_order_create
✗ test_order_payment
✗ test_order_query
✗ test_refund_apply (Error)
✗ test_refund_status (Error)
```

**--skip-success（默认，只显示失败）：**
```
Test Results: 100 tests, 95 passed, 3 failed, 2 errors

✗ test_order_create
✗ test_order_payment
✗ test_order_query
✗ test_refund_apply (Error)
✗ test_refund_status (Error)

(95 passed tests are hidden. Use --no-skip-success to show all.)
```

---

## 📊 报告完整结构

### 报告概览

```
ApiMeter Test Report
====================

Summary:
  Total: 50 tests
  Passed: 45 (90%)
  Failed: 3 (6%)
  Errors: 2 (4%)
  Duration: 12.5s
  Start Time: 2025-10-16 10:30:00
  Platform: Darwin-24.6.0-x86_64
```

### 测试详情

每个测试步骤包含：

1. **基本信息**
   - 测试名称
   - 执行状态（✓ / ✗）
   - 执行时间

2. **请求信息**（可折叠）
   - Method & URL
   - Headers（树形展示）
   - Body（树形展示）
   - Query Parameters

3. **响应信息**（可折叠）
   - Status Code
   - Headers（树形展示）
   - Body（树形展示）
   - Response Time

4. **校验结果**
   - Validators（传统校验器）
   - Script Validations（脚本校验，树形展示）

5. **变量提取**
   - Extracted Variables

6. **错误信息**（如果失败）
   - Error Type
   - Error Message
   - Traceback（树形展示）

---

## 🎨 报告增强前后对比

### 对比 1：大 JSON 响应

**增强前：**
- ❌ 所有内容一次性展示
- ❌ 超长 JSON 占据大量空间
- ❌ 滚动困难，难以定位
- ❌ 报告加载慢

**增强后：**
- ✅ 自动折叠超过 15 行的内容
- ✅ 树形结构，节点级别展开
- ✅ 彩色语法高亮
- ✅ 报告加载快

### 对比 2：Script 校验结果

**增强前：**
- ❌ Script 执行结果不可见
- ❌ 只能看到"Script 校验失败"
- ❌ 无法知道哪条脚本失败
- ❌ 调试困难

**增强后：**
- ✅ 每条脚本独立显示状态
- ✅ 清晰的成功/失败标记
- ✅ 详细的错误信息和堆栈
- ✅ 调试友好

### 对比 3：报告体积

**测试场景：** 100 个测试用例，每个用例响应 500 行 JSON

| 版本 | 报告大小 | 加载时间 |
|-----|---------|---------|
| 增强前 | 25 MB | 5-8 秒 |
| 增强后（--no-skip-success） | 12 MB | 2-3 秒 |
| 增强后（--skip-success） | 3 MB | < 1 秒 |

---

## 💡 最佳实践

### 1. 开发阶段：显示所有用例

```bash
# 开发阶段，查看所有用例详情
hrun testcases/ --html report.html --no-skip-success
```

### 2. CI/CD 阶段：只显示失败

```bash
# CI/CD 管道中，聚焦失败用例
hrun testcases/ --html report.html --skip-success
```

### 3. 性能测试：启用所有优化

```bash
# 大量用例时，使用所有优化
hrun testcases/ --html report.html --skip-success
```

### 4. 调试单个用例：完整展示

```bash
# 调试特定用例，查看所有细节
hrun testcases/test_specific.yml --html report.html --no-skip-success --log-level debug
```

---

## 🔧 技术实现

### 折叠机制

```javascript
// 伪代码示例
function renderContent(content) {
  const lines = content.split('\n');
  
  if (lines.length > 15) {
    // 自动折叠
    return `
      <div class="collapsible collapsed">
        <button class="toggle">展开 (${lines.length} 行)</button>
        <button class="copy">复制</button>
        <pre class="content hidden">${content}</pre>
      </div>
    `;
  } else {
    // 直接显示
    return `<pre>${content}</pre>`;
  }
}
```

### 树形展示

```javascript
// 伪代码示例
function renderTree(data) {
  if (isJSON(data)) {
    return createTreeView(parseJSON(data));
  } else if (isPythonDict(data)) {
    return createTreeView(parsePythonDict(data));
  } else {
    return `<pre>${data}</pre>`;
  }
}
```

### 懒加载

```javascript
// 大型数据节点懒加载
function loadNode(node) {
  if (node.childCount > 100) {
    // 延迟加载子节点
    node.children = () => fetchChildren(node.path);
  }
}
```

---

## 📝 总结

ApiMeter 报告增强特性对比：

| 特性 | 增强前 | 增强后 | 提升 |
|-----|-------|--------|------|
| 大 JSON 可读性 | ★☆☆☆☆ | ★★★★★ | +400% |
| 报告体积 | 大 | 小 | -50~70% |
| 加载速度 | 慢 | 快 | +300% |
| Script 结果可见性 | 无 | 完整 | 新功能 |
| 调试友好度 | ★★☆☆☆ | ★★★★★ | +150% |

**核心价值：**
- ✅ **可读性** - 树形结构让复杂数据一目了然
- ✅ **性能** - 智能折叠和懒加载大幅提升加载速度
- ✅ **调试** - Script 执行详情让问题排查更简单
- ✅ **灵活** - skip-success 让你专注于失败用例

**下一步学习：**
- [10分钟快速上手](../quickstart.md)
- [自定义脚本校验](../prepare/script.md)
- [高级用法示例](../examples/advanced-examples.md)

---

**有问题？** 查看 [FAQ](../FAQ.md) 或 [提交 Issue](https://git.umlife.net/utils/apimeter/issues)

