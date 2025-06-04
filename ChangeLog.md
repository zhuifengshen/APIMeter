 # ChangeLog 
 
 HttpRunner v2.5.9 之后扩展功能
 

## 一、支持测试报告瘦身

apimeter /path/to/api --skip-success  # 报告忽略成功用例数


## 二、自定义函数参数支持列表和字典

## 问题描述

在HttpRunner v2.5.9中，当测试用例中的自定义函数参数为列表或对象时，无法正常解析。具体表现为：

1. `${get_sign_v2([$device_sn, $os_platform, $app_version])}` 无法匹配
2. `${get_sign_v3({"device_sn": $device_sn, "os_platform": $os_platform, "app_version": $app_version})}` 无法匹配
3. 即使匹配成功，参数也会被错误地分割成多个独立参数

## 根本原因

1. **正则表达式限制**：原有的函数正则表达式 `\$\{(\w+)\(([\$\w\.\-/\s=,]*)\)\}` 不支持方括号 `[]` 和花括号 `{}`
2. **参数解析问题**：`parse_function_params` 函数使用简单的逗号分割，无法处理嵌套的列表和对象结构
3. **类型转换缺失**：解析后的字符串参数没有被转换为实际的数据结构

## 修复方案

### 1. 更新正则表达式

```python
# 原来的正则表达式
function_regex_compile = re.compile(r"\$\{(\w+)\(([\$\w\.\-/\s=,]*)\)\}")

# 修复后的正则表达式
function_regex_compile = re.compile(r"\$\{(\w+)\(([^)]*)\)\}")
```

新的正则表达式使用 `[^)]*` 来匹配除了右括号之外的所有字符，支持更复杂的参数格式。

### 2. 智能参数分割

新增 `smart_split_params` 函数，能够智能地分割函数参数，考虑嵌套的括号和引号：

```python
def smart_split_params(params_str):
    """智能分割函数参数，考虑嵌套的括号和引号"""
    # 实现细节见代码
```

### 3. 增强参数解析

重写 `parse_function_params` 函数：
- 使用智能分割替代简单的逗号分割
- 正确处理等号在引号内的情况
- 保持向后兼容性

### 4. 类型转换支持

在 `LazyFunction.to_value` 方法中新增类型转换逻辑：
- 检测列表格式的字符串参数 `[...]`
- 检测字典格式的字符串参数 `{...}`
- 将变量替换后的字符串转换为有效的Python字面量
- 使用 `ast.literal_eval` 安全地解析为实际的数据结构

## 修复效果

### 修复前
```python
# ${get_sign_v2([$device_sn, $os_platform, $app_version])}
# 无法匹配，或者被错误解析为3个独立参数
```

### 修复后
```python
# ${get_sign_v2([$device_sn, $os_platform, $app_version])}
# 正确解析为单个列表参数: ['TESTCASE_SETUP_XXX', 'ios', '2.8.6']

# ${get_sign_v3({"device_sn": $device_sn, "os_platform": $os_platform, "app_version": $app_version})}
# 正确解析为单个字典参数: {'device_sn': 'TESTCASE_SETUP_XXX', 'os_platform': 'ios', 'app_version': '2.8.6'}
```

## 向后兼容性

所有原有的函数调用格式仍然正常工作：
- `${func(1, 2, 3)}` ✅
- `${func(a=1, b=2)}` ✅
- `${func($var1, $var2)}` ✅

## 测试验证

修复包含了完整的测试验证：
1. 原有功能兼容性测试 - 全部通过
2. 新增功能测试 - 全部通过
3. 实际使用场景测试 - 全部通过

## 文件修改

主要修改文件：`apimeter/parser.py`

- 更新了函数正则表达式
- 新增了 `smart_split_params` 函数
- 重写了 `parse_function_params` 函数
- 增强了 `LazyFunction.to_value` 方法
- 新增了 `_convert_to_python_literal` 方法

## 额外修复

### YAML语法问题
在测试过程中发现，当函数参数包含花括号 `{}` 时，YAML解析器会将其误认为是字典定义，导致语法错误：
```
ERROR    mapping values are not allowed here
```

**解决方案**：将包含复杂参数的函数调用用引号包围：
```yaml
# 错误写法
sign: ${get_sign_v3({"device_sn": $device_sn, "os_platform": $os_platform, "app_version": $app_version})}

# 正确写法  
sign: "${get_sign_v3({\"device_sn\": $device_sn, \"os_platform\": $os_platform, \"app_version\": $app_version})}"
```

更多示例
```yaml
sign: ${get_sign($device_sn, $os_platform, $app_version)}

sign: "${get_sign_v2([$device_sn, $os_platform, $app_version])}"
sign: ${get_sign_v2([$device_sn, $os_platform, $app_version])}

sign: "${get_sign_v3({device_sn: $device_sn, os_platform: $os_platform, app_version: $app_version})}"
sign: "${get_sign_v3({'device_sn': $device_sn, 'os_platform': $os_platform, 'app_version': $app_version})}"
sign: "${get_sign_v3({\"device_sn\": $device_sn, \"os_platform\": $os_platform, \"app_version\": $app_version})}"
```


### Python兼容性问题
修复了Python 3.11兼容性问题：
```python
# 原来的代码
from collections import Iterable

# 修复后的代码
try:
    from collections.abc import Iterable
except ImportError:
    from collections import Iterable
```

## 使用示例

修复后，以下用法都能正常工作：

```yaml
# demo/setup.yml
teststeps:
-
    name: get token (setup)
    request:
        url: /api/get-token
        json:
            # 列表参数 - 现在可以正常工作（需要引号）
            sign: "${get_sign_v2([$device_sn, $os_platform, $app_version])}"
            # 字典参数 - 现在可以正常工作（需要引号和转义）
            sign: "${get_sign_v3({\"device_sn\": $device_sn, \"os_platform\": $os_platform, \"app_version\": $app_version})}"
            # 原有格式 - 继续正常工作
            sign: ${get_sign($device_sn, $os_platform, $app_version)}
```

## 验证测试

所有三种格式都已验证可以正常工作：

1. **原有多参数格式**：`sign v1: 9e2d1dab9fffdbe8a6d4858ae93cdca9a4cc9d14` ✅
2. **列表参数格式**：`sign v2: 9e2d1dab9fffdbe8a6d4858ae93cdca9a4cc9d14` ✅  
3. **字典参数格式**：`sign v3: 9e2d1dab9fffdbe8a6d4858ae93cdca9a4cc9d14` ✅