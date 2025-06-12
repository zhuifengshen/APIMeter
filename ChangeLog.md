 # ChangeLog 

## HttpRunner v2.5.9 之后扩展功能，支持以下所有函数调用格式：
1. 原始格式: ${get_sign($device_sn, $os_platform, $app_version)}
2. 列表参数: ${get_sign_v2([$device_sn, $os_platform, $app_version])}
3. 字典参数: ${get_sign_v3({device_sn: $device_sn, os_platform: $os_platform, app_version: $app_version})}
4. 响应对象: ${validate_token_v2(content)}
5. 响应路径: ${validate_token(content.token)}
6. 变量属性: ${validate_token($resp.token)}


## 自定义函数调用的正确语法格式
```yaml
# 一、校验器中自定义函数调用的正确语法格式
✅ 正确写法1：多行格式
validate:
  - eq: 
    - ${validate_token($token)}
    - true
✅ 正确写法2：单行格式（加引号）
validate:
  - eq: ["${validate_token($token)}", true]
❌ 错误写法：单行格式（无引号）
validate:
  - eq: [${validate_token($token)}, true]  # 这会导致YAML解析错误

# 二、对于包含字典参数的自定义函数调用的正确语法格式
✅ 正确方法1：使用双引号和转义
sign: "${get_sign_v3({\"device_sn\": $device_sn, \"os_platform\": $os_platform})}"

✅ 正确方法2：使用单引号（如果变量不包含单引号）
sign: "${get_sign_v3({'device_sn': $device_sn, 'os_platform': $os_platform})}"

✅ 正确方法3：YAML原生字典语法（推荐）
sign: "${get_sign_v3({device_sn: $device_sn, os_platform: $os_platform})}"

❌ 错误写法：无引号
sign: ${get_sign_v3({"device_sn": $device_sn, "os_platform": $os_platform, "app_version": $app_version})}

# 三、对于包含列表参数的函数调用的正确语法格式
sign: ${get_sign($device_sn, $os_platform, $app_version)}
sign: "${get_sign_v2([$device_sn, $os_platform, $app_version])}"
sign: ${get_sign_v2([$device_sn, $os_platform, $app_version])}

# 四、其他注意事项
1. content是全局默认响应体变量，不需要使用美元符号 $content；
```



# 附录-详细内容

# 一、支持测试报告瘦身

apimeter /path/to/api --skip-success  # 报告忽略成功用例数


# 二、自定义函数参数支持列表和字典

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



# 三、函数调用在YAML中的正确写法

### 问题描述1
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

### 字典参数的特殊处理

对于包含字典参数的函数调用，有多种写法：

```yaml
# 方法1：使用双引号和转义
sign: "${get_sign_v3({\"device_sn\": $device_sn, \"os_platform\": $os_platform})}"

# 方法2：使用单引号（如果变量不包含单引号）
sign: "${get_sign_v3({'device_sn': $device_sn, 'os_platform': $os_platform})}"

# 方法3：YAML原生字典语法（推荐）
sign: "${get_sign_v3({device_sn: $device_sn, os_platform: $os_platform})}"
```

另外，对于包含列表参数的函数调用方式如下：
```yaml
sign: ${get_sign($device_sn, $os_platform, $app_version)}
sign: "${get_sign_v2([$device_sn, $os_platform, $app_version])}"
sign: ${get_sign_v2([$device_sn, $os_platform, $app_version])}
```


### 问题描述2

当在YAML的列表（数组）语法中使用包含特殊字符的函数调用时，可能会遇到解析错误：

```
ERROR    while parsing a flow sequence
expected ',' or ']', but got '{'
```

### 解决方案

#### ✅ 正确写法1：多行格式

```yaml
validate:
  - eq: 
    - ${validate_token($token)}
    - true
```

#### ✅ 正确写法2：单行格式（加引号）

```yaml
validate:
  - eq: ["${validate_token($token)}", true]
```

#### ❌ 错误写法：单行格式（无引号）

```yaml
validate:
  - eq: [${validate_token($token)}, true]  # 这会导致YAML解析错误
```

### 规则总结

1. **多行格式**：总是安全的，推荐用于复杂的函数调用
2. **单行格式**：当函数调用包含特殊字符（如 `{`, `}`, `[`, `]`）时，必须用引号包围
3. **简单函数调用**：如 `${func()}` 在单行格式中通常不需要引号

### 实际示例

```yaml
# 各种函数调用的正确写法
teststeps:
-
    name: test functions
    validate:
        # 简单函数调用 - 无需引号
        - eq: [${get_timestamp()}, 1234567890]
        
        # 复杂函数调用 - 需要引号
        - eq: ["${validate_data({\"key\": $value})}", true]
        
        # 列表参数 - 需要引号
        - eq: ["${process_list([$item1, $item2])}", "success"]
        
        # 多行格式 - 总是安全
        - eq:
          - ${complex_function($param1, $param2)}
          - expected_result
```

### 最佳实践

1. **优先使用多行格式**：更清晰，不容易出错
2. **复杂参数加引号**：包含 `{}[]` 等特殊字符时
3. **保持一致性**：在同一个项目中使用统一的风格
4. **测试验证**：修改YAML后及时验证语法正确性




# 四、Python兼容性问题
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

## 1、安装 apimeter 报错
```
pip install apimeter
Collecting apimeter
  Downloading apimeter-2.6.2-py2.py3-none-any.whl (79 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 79.4/79.4 kB 322.5 kB/s eta 0:00:00
Collecting requests-toolbelt<0.10.0,>=0.9.1
  Downloading requests_toolbelt-0.9.1-py2.py3-none-any.whl (54 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 54.3/54.3 kB 157.1 kB/s eta 0:00:00
Collecting requests<3.0.0,>=2.22.0
  Downloading requests-2.32.3-py3-none-any.whl (64 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 64.9/64.9 kB 175.8 kB/s eta 0:00:00
Collecting jsonschema<4.0.0,>=3.2.0
  Downloading jsonschema-3.2.0-py2.py3-none-any.whl (56 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 56.3/56.3 kB 147.8 kB/s eta 0:00:00
Collecting jsonpath<0.83,>=0.82
  Downloading jsonpath-0.82.2.tar.gz (10 kB)
  Preparing metadata (setup.py) ... done
Collecting filetype<2.0.0,>=1.0.5
  Downloading filetype-1.2.0-py2.py3-none-any.whl (19 kB)
Collecting pyyaml<6.0.0,>=5.1.2
  Downloading PyYAML-5.4.1.tar.gz (175 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 175.1/175.1 kB 278.0 kB/s eta 0:00:00
  Installing build dependencies ... error
  error: subprocess-exited-with-error

  × pip subprocess to install build dependencies did not run successfully.
  │ exit code: 2
  ╰─> [84 lines of output]
      Collecting setuptools
        Downloading setuptools-75.8.2-py3-none-any.whl (1.2 MB)
           ━━━━━━━━━━━━━━━━━╸                       0.6/1.2 MB 6.4 kB/s eta 0:01:46
      ERROR: Exception:
      Traceback (most recent call last):
        File "/Users/devin/.pyenv/versions/3.9.21/envs/gx_hrun_3.9.21/lib/python3.9/site-packages/pip/_vendor/urllib3/response.py", line 438, in _error_catcher
          yield
        File "/Users/devin/.pyenv/versions/3.9.21/envs/gx_hrun_3.9.21/lib/python3.9/site-packages/pip/_vendor/urllib3/response.py", line 561, in read
          data = self._fp_read(amt) if not fp_closed else b""
        File "/Users/devin/.pyenv/versions/3.9.21/envs/gx_hrun_3.9.21/lib/python3.9/site-packages/pip/_vendor/urllib3/response.py", line 527, in _fp_read
          return self._fp.read(amt) if amt is not None else self._fp.read()
        File "/Users/devin/.pyenv/versions/3.9.21/envs/gx_hrun_3.9.21/lib/python3.9/site-packages/pip/_vendor/cachecontrol/filewrapper.py", line 90, in read
          data = self.__fp.read(amt)
        File "/Users/devin/.pyenv/versions/3.9.21/lib/python3.9/http/client.py", line 463, in read
          n = self.readinto(b)
        File "/Users/devin/.pyenv/versions/3.9.21/lib/python3.9/http/client.py", line 507, in readinto
          n = self.fp.readinto(b)
        File "/Users/devin/.pyenv/versions/3.9.21/lib/python3.9/socket.py", line 716, in readinto
          return self._sock.recv_into(b)
        File "/Users/devin/.pyenv/versions/3.9.21/lib/python3.9/ssl.py", line 1275, in recv_into
          return self.read(nbytes, buffer)
        File "/Users/devin/.pyenv/versions/3.9.21/lib/python3.9/ssl.py", line 1133, in read
          return self._sslobj.read(len, buffer)
      socket.timeout: The read operation timed out

      During handling of the above exception, another exception occurred:

      Traceback (most recent call last):
        File "/Users/devin/.pyenv/versions/3.9.21/envs/gx_hrun_3.9.21/lib/python3.9/site-packages/pip/_internal/cli/base_command.py", line 160, in exc_logging_wrapper
          status = run_func(*args)
        File "/Users/devin/.pyenv/versions/3.9.21/envs/gx_hrun_3.9.21/lib/python3.9/site-packages/pip/_internal/cli/req_command.py", line 247, in wrapper
          return func(self, options, args)
        File "/Users/devin/.pyenv/versions/3.9.21/envs/gx_hrun_3.9.21/lib/python3.9/site-packages/pip/_internal/commands/install.py", line 419, in run
          requirement_set = resolver.resolve(
        File "/Users/devin/.pyenv/versions/3.9.21/envs/gx_hrun_3.9.21/lib/python3.9/site-packages/pip/_internal/resolution/resolvelib/resolver.py", line 92, in resolve
          result = self._result = resolver.resolve(
        File "/Users/devin/.pyenv/versions/3.9.21/envs/gx_hrun_3.9.21/lib/python3.9/site-packages/pip/_vendor/resolvelib/resolvers.py", line 481, in resolve
          state = resolution.resolve(requirements, max_rounds=max_rounds)
        File "/Users/devin/.pyenv/versions/3.9.21/envs/gx_hrun_3.9.21/lib/python3.9/site-packages/pip/_vendor/resolvelib/resolvers.py", line 348, in resolve
          self._add_to_criteria(self.state.criteria, r, parent=None)
        File "/Users/devin/.pyenv/versions/3.9.21/envs/gx_hrun_3.9.21/lib/python3.9/site-packages/pip/_vendor/resolvelib/resolvers.py", line 172, in _add_to_criteria
          if not criterion.candidates:
        File "/Users/devin/.pyenv/versions/3.9.21/envs/gx_hrun_3.9.21/lib/python3.9/site-packages/pip/_vendor/resolvelib/structs.py", line 151, in __bool__
          return bool(self._sequence)
        File "/Users/devin/.pyenv/versions/3.9.21/envs/gx_hrun_3.9.21/lib/python3.9/site-packages/pip/_internal/resolution/resolvelib/found_candidates.py", line 155, in __bool__
          return any(self)
        File "/Users/devin/.pyenv/versions/3.9.21/envs/gx_hrun_3.9.21/lib/python3.9/site-packages/pip/_internal/resolution/resolvelib/found_candidates.py", line 143, in <genexpr>
          return (c for c in iterator if id(c) not in self._incompatible_ids)
        File "/Users/devin/.pyenv/versions/3.9.21/envs/gx_hrun_3.9.21/lib/python3.9/site-packages/pip/_internal/resolution/resolvelib/found_candidates.py", line 47, in _iter_built
          candidate = func()
        File "/Users/devin/.pyenv/versions/3.9.21/envs/gx_hrun_3.9.21/lib/python3.9/site-packages/pip/_internal/resolution/resolvelib/factory.py", line 206, in _make_candidate_from_link
          self._link_candidate_cache[link] = LinkCandidate(
        File "/Users/devin/.pyenv/versions/3.9.21/envs/gx_hrun_3.9.21/lib/python3.9/site-packages/pip/_internal/resolution/resolvelib/candidates.py", line 297, in __init__
          super().__init__(
        File "/Users/devin/.pyenv/versions/3.9.21/envs/gx_hrun_3.9.21/lib/python3.9/site-packages/pip/_internal/resolution/resolvelib/candidates.py", line 162, in __init__
          self.dist = self._prepare()
        File "/Users/devin/.pyenv/versions/3.9.21/envs/gx_hrun_3.9.21/lib/python3.9/site-packages/pip/_internal/resolution/resolvelib/candidates.py", line 231, in _prepare
          dist = self._prepare_distribution()
        File "/Users/devin/.pyenv/versions/3.9.21/envs/gx_hrun_3.9.21/lib/python3.9/site-packages/pip/_internal/resolution/resolvelib/candidates.py", line 308, in _prepare_distribution
          return preparer.prepare_linked_requirement(self._ireq, parallel_builds=True)
        File "/Users/devin/.pyenv/versions/3.9.21/envs/gx_hrun_3.9.21/lib/python3.9/site-packages/pip/_internal/operations/prepare.py", line 491, in prepare_linked_requirement
          return self._prepare_linked_requirement(req, parallel_builds)
        File "/Users/devin/.pyenv/versions/3.9.21/envs/gx_hrun_3.9.21/lib/python3.9/site-packages/pip/_internal/operations/prepare.py", line 536, in _prepare_linked_requirement
          local_file = unpack_url(
        File "/Users/devin/.pyenv/versions/3.9.21/envs/gx_hrun_3.9.21/lib/python3.9/site-packages/pip/_internal/operations/prepare.py", line 166, in unpack_url
          file = get_http_url(
        File "/Users/devin/.pyenv/versions/3.9.21/envs/gx_hrun_3.9.21/lib/python3.9/site-packages/pip/_internal/operations/prepare.py", line 107, in get_http_url
          from_path, content_type = download(link, temp_dir.path)
        File "/Users/devin/.pyenv/versions/3.9.21/envs/gx_hrun_3.9.21/lib/python3.9/site-packages/pip/_internal/network/download.py", line 147, in __call__
          for chunk in chunks:
        File "/Users/devin/.pyenv/versions/3.9.21/envs/gx_hrun_3.9.21/lib/python3.9/site-packages/pip/_internal/cli/progress_bars.py", line 53, in _rich_progress_bar
          for chunk in iterable:
        File "/Users/devin/.pyenv/versions/3.9.21/envs/gx_hrun_3.9.21/lib/python3.9/site-packages/pip/_internal/network/utils.py", line 63, in response_chunks
          for chunk in response.raw.stream(
        File "/Users/devin/.pyenv/versions/3.9.21/envs/gx_hrun_3.9.21/lib/python3.9/site-packages/pip/_vendor/urllib3/response.py", line 622, in stream
          data = self.read(amt=amt, decode_content=decode_content)
        File "/Users/devin/.pyenv/versions/3.9.21/envs/gx_hrun_3.9.21/lib/python3.9/site-packages/pip/_vendor/urllib3/response.py", line 587, in read
          raise IncompleteRead(self._fp_bytes_read, self.length_remaining)
        File "/Users/devin/.pyenv/versions/3.9.21/lib/python3.9/contextlib.py", line 137, in __exit__
          self.gen.throw(typ, value, traceback)
        File "/Users/devin/.pyenv/versions/3.9.21/envs/gx_hrun_3.9.21/lib/python3.9/site-packages/pip/_vendor/urllib3/response.py", line 443, in _error_catcher
          raise ReadTimeoutError(self._pool, None, "Read timed out.")
      pip._vendor.urllib3.exceptions.ReadTimeoutError: HTTPSConnectionPool(host='files.pythonhosted.org', port=443): Read timed out.
      Could not fetch URL https://pypi.org/simple/pip/: There was a problem confirming the ssl certificate: HTTPSConnectionPool(host='pypi.org', port=443): Max retries exceeded with url: /simple/pip/ (Caused by SSLError(SSLZeroReturnError(6, 'TLS/SSL connection has been closed (EOF) (_ssl.c:1147)'))) - skipping
      [end of output]

  note: This error originates from a subprocess, and is likely not a problem with pip.
error: subprocess-exited-with-error

× pip subprocess to install build dependencies did not run successfully.
│ exit code: 2
╰─> See above for output.

note: This error originates from a subprocess, and is likely not a problem with pip.
```

原因：安装依赖 PyYAML==5.41 时编译出错。

解决方法：直接安装之前兼容的版本 pip3 install PyYAML==5.31，然后再执行 pip3 install apimeter 即可。


## 2、命令 apimeter -V 报错
```
Traceback (most recent call last):
  File "/Users/devin/.pyenv/versions/gx_hrun_3.9.21/bin/hrun", line 5, in <module>
    from apimeter.cli import main
  File "/Users/devin/.pyenv/versions/gx_hrun_3.9.21/lib/python3.9/site-packages/apimeter/cli.py", line 8, in <module>
    from apimeter.api import HttpRunner
  File "/Users/devin/.pyenv/versions/gx_hrun_3.9.21/lib/python3.9/site-packages/apimeter/api.py", line 5, in <module>
    from apimeter import (
  File "/Users/devin/.pyenv/versions/gx_hrun_3.9.21/lib/python3.9/site-packages/apimeter/report/__init__.py", line 10, in <module>
    from apimeter.report.stringify import stringify_summary
  File "/Users/devin/.pyenv/versions/gx_hrun_3.9.21/lib/python3.9/site-packages/apimeter/report/stringify.py", line 4, in <module>
    from jinja2 import escape
  File "/Users/devin/.pyenv/versions/gx_hrun_3.9.21/lib/python3.9/site-packages/jinja2/__init__.py", line 12, in <module>
    from .environment import Environment
  File "/Users/devin/.pyenv/versions/gx_hrun_3.9.21/lib/python3.9/site-packages/jinja2/environment.py", line 25, in <module>
    from .defaults import BLOCK_END_STRING
  File "/Users/devin/.pyenv/versions/gx_hrun_3.9.21/lib/python3.9/site-packages/jinja2/defaults.py", line 3, in <module>
    from .filters import FILTERS as DEFAULT_FILTERS  # noqa: F401
  File "/Users/devin/.pyenv/versions/gx_hrun_3.9.21/lib/python3.9/site-packages/jinja2/filters.py", line 13, in <module>
    from markupsafe import soft_unicode
ImportError: cannot import name 'soft_unicode' from 'markupsafe' (/Users/devin/.pyenv/versions/gx_hrun_3.9.21/lib/python3.9/site-packages/markupsafe/__init__.py)
```

原因：jinja2 依赖库 markusafe 不兼容，需要降级版本

解决方法：
在 pyproject.toml 的 [tool.poetry.dependencies] 部分中添加：
markupsafe = "2.0.1"
jinja2 = "2.10.3"


## 3、在APIMeter v2.7.1版本中调整为Python3.6+
实际使用过程中，都是python3的环境的。但如果有需要，调整Python版本号，依旧可以在2.7+环境中正常使用。


## 4、从Python 3.9.21切换到Python 3.11.11后，运行单元测试出现以下兼容性问题

1. **collections.Hashable 导入错误**
   ```
   AttributeError: module 'collections' has no attribute 'Hashable'
   ```

2. **HTTP headers 大小写敏感性问题**
   - 某些测试期望特定的header名称大小写，但实际返回的可能不同

### 修复方案

#### 1. collections.Hashable 兼容性修复

**问题原因**: 在Python 3.10+中，`collections.Hashable` 被移动到了 `collections.abc.Hashable`

**修复文件**: 
- `apimeter/parser.py`
- `apimeter/utils.py`

**修复内容**:

```python
# apimeter/parser.py
try:
    # Python 3.10+ 中 collections.Hashable 被移动到 collections.abc
    from collections.abc import Hashable
except ImportError:
    # Python < 3.10 兼容性
    from collections import Hashable

# 使用 Hashable 替代 collections.Hashable
if not isinstance(validator["check"], Hashable):
```

```python
# apimeter/utils.py
try:
    # Python 3.10+ 中一些collections类型被移动到 collections.abc
    from collections.abc import Iterable
    collections_deque = collections.deque
except ImportError:
    # Python < 3.10 兼容性
    from collections import Iterable
    collections_deque = collections.deque

# 使用 collections_deque 替代 collections.deque
if isinstance(value, (tuple, collections_deque)):
```

#### 2. HTTP Headers 大小写不敏感匹配

**问题原因**: HTTP headers在不同服务器实现中可能有不同的大小写

**修复文件**: `apimeter/response.py`

**修复内容**:

```python
# headers
elif top_query == "headers":
    headers = self.headers
    if not sub_query:
        # extract headers
        return headers

    # 首先尝试直接匹配
    if sub_query in headers:
        return headers[sub_query]
    
    # 如果直接匹配失败，尝试大小写不敏感匹配
    for header_key, header_value in headers.items():
        if header_key.lower() == sub_query.lower():
            return header_value
    
    # 如果都失败了，抛出异常
    err_msg = "Failed to extract header! => {}\n".format(field)
    err_msg += "response headers: {}\n".format(headers)
    logger.log_error(err_msg)
    raise exceptions.ExtractFailure(err_msg)
```

#### 3. CI/CD 配置更新

**更新文件**:
- `.github/workflows/unittest.yml`
- `.github/workflows/smoketest.yml`

**主要改进**:
- 支持Python 3.6-3.12版本测试
- 使用最新的GitHub Actions版本
- 添加兼容性测试步骤
- 优化缓存策略

### 使用建议

1. **本地开发**: 使用 `make test` 验证兼容性
2. **CI/CD**: GitHub Actions会自动测试所有支持的Python版本
3. **部署**: 确保目标环境Python版本在3.6+范围内