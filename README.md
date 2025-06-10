# ApiMeter

*ApiMeter* is a simple & elegant, yet powerful HTTP(S) testing framework. Enjoy! ✨ 🚀 ✨


## Usage
```python
pip install apimeter  # 安装
apimeter /path/to/api  # 完整生成报告
apimeter /path/to/api --skip-success  # 报告忽略成功用例数
```
注意事项
- 1、安装后可用命令apimeter、hrun、apilocust；
- 2、安装时不需要卸载HttpRunner，如果存在httprunner，会覆盖其hrun命令，另外的httprunner、ate命令依然可用；
- 3、之所以不卸载HttpRunner，因为部分项目在debugtalk.py中导入了HttpRunner包并使用其已封装好的函数；

## Document

ApiMeter 用户使用文档：[https://utils.git.umlife.net/apimeter](https://utils.git.umlife.net/apimeter/)

## Development
```python
# 本地开发与运行
poetry install  # 拉取代码后安装依赖
poetry run python -m apimeter /path/to/api  # 完整生成报告
poetry run python -m apimeter /path/to/api --skip-success  # 报告忽略成功用例数据
python -m apimeter -h # 查看使用指南

# 测试运行
python -m unittest discover # 运行所有单元测试
python -m unittest tests/test_context.py # 运行指定测试文件

python tests/api_server.py # 启动测试示例服务器
python -m apimeter tests/demo/demo.yml
python -m apimeter tests/testcases --log-level debug --save-tests # 测试示例，同时设置日志与生成中间处理文件

# 打包编译与发布
git tag v1.0.0 或 git tag -a v1.0.0 -m "发布正式版本 v1.0.0" # 打标签（轻量或附注）
git push v1.0.0 或 git push --tags # 推送标签(单个或所有)
poetry build  # 打包
poetry publish  # 发布，根据提示输入pypi账号密码
pip install -i https://pypi.Python.org/simple/ apimeter  # 指定安装源，因为刚发布其他平台未及时同步


# 文档编译与部署 .gitlab-ci.yml(apimeter-部署-Pages)
pip install mkdocs-material==3.3.0
mkdocs build
mkdocs serve


# 如何将git项目本地的report分支推送到远程的master分支
git checkout report
git push origin report:master


# 逐行代码运行时内存分析
poetry shell
pip install memory-profiler
# 1. 导入方式
python -m apimeter /Users/zhangchuzhao/Project/ATDD/tmp/demo_api/ --skip-success
# 2. 装饰器方式
python -m memory_profiler apimeter /Users/zhangchuzhao/Project/ATDD/tmp/demo_api --skip-success --log-level error
# 3. 命令方式
mprof run apimeter /path/to/api
mprof plot  # 生成内存趋势图，安装依赖pip install matplotlib
# 参考链接：https://www.cnblogs.com/rgcLOVEyaya/p/RGC_LOVE_YAYA_603days_1.html
```


[Requests]: http://docs.python-requests.org/en/master/
[unittest]: https://docs.python.org/3/library/unittest.html
[Locust]: http://locust.io/
[har2case]: https://github.com/httprunner/har2case
[HAR]: http://httparchive.org/
[Swagger]: https://swagger.io/

## Validate

### 1、校验器支持两种格式
```
- {"check": check_item, "comparator": comparator_name, "expect": expect_value}  # 一般格式
- comparator_name: [check_item, expect_value]  # 简化格式
```

### 2、支持自定义校验器
对于自定义的校验函数，需要遵循三个规则：
- (1)自定义校验函数需放置到debugtalk.py中;
- (2)参数有两个：第一个为原始数据，第二个为原始数据经过运算后得到的预期结果值;
- (3)在校验函数中通过assert将实际运算结果与预期结果值进行比较;
```
# 用例
- test:
    name: get token
    request:
        url: http://127.0.0.1:5000/api/get-token
        method: GET
    validate:
        - {"check": "status_code", "comparator": "eq", "expect": 200}
        - {"check": "status_code", "comparator": "sum_status_code", "expect": 2}

# 自定义校验器
def sum_status_code(status_code, expect_sum):
    """ sum status code digits
        e.g. 400 => 4, 201 => 3
    """
    sum_value = 0
    for digit in str(status_code):
        sum_value += int(digit)
    assert sum_value == expect_sum
```

### 3、支持在校验器中引用变量
在结果校验器validate中，check和expect均可实现实现变量的引用；而引用的变量，可以来自四种类型：
- （1）当前test中定义的variables，例如expect_status_code
- （2）当前test中提取（extract）的结果变量，例如token
- （3）当前测试用例集testset中，先前test中提取（extract）的结果变量
- （4）当前测试用例集testset中，全局配置config中定义的变量
```
- test:
    name: get token
    request:
      url: http://127.0.0.1:5000/api/get_token
      method: GET
    variables:
      - expect_status_code: 200
      - token_len: 16
    extract:
      - token: content.token
    validate:
      - {"check": "status_code", "comparator": "eq", “expect": "$expect_status_code"}
      - {"check": "content.token", "comparator": "len_eq", "expect": "$token_len"}
      - {"check": "$token", "comparator": "len_eq", "expect": "$token_len"}
```
基于引用变量的特效，可实现更灵活的自定义函数校验器
```
- test:
    name: get token
    request:
        url: http://127.0.0.1:5000/api/get-token
        method: GET
    validate:
        - {"check": "status_code", "comparator": "eq", "expect": 200}
        - {"check": "${sum_status_code(status_code)}", "comparator": "eq", "expect": 2}

# 自定义函数
def sum_status_code(status_code):
    """ sum status code digits
        e.g. 400 => 4, 201 => 3
    """
    sum_value = 0
    for digit in str(status_code):
        sum_value += int(digit)
    return sum_value
```

### 4、支持正则表达式提取结果校验内容
假设接口的响应结果内容为LB123abcRB789，那么要提取出abc部分进行校验：
```
- test:
    name: get token
    request:
        url: http://127.0.0.1:5000/api/get-token
        method: GET
    validate:
        - {"check": "LB123(.*)RB789", "comparator": "eq", "expect": "abc"}
```

### 5、内置校验器
| Comparator         | Description                     | A(check), B(expect)           | Examples                        |
|-------------------|--------------------------------|------------------------------|--------------------------------|
| eq, ==           | value is equal                 | A == B                       | 9 eq 9                        |
| lt              | less than                      | A < B                        | 7 lt 8                        |
| le              | less than or equals            | A <= B                       | 7 le 8, 8 le 8                |
| gt              | greater than                   | A > B                        | 8 gt 7                        |
| ge              | greater than or equals         | A >= B                       | 8 ge 7, 8 ge 8                |
| ne              | not equals                     | A != B                       | 6 ne 9                        |
| str_eq          | string equals                  | str(A) == str(B)             | 123 str_eq '123'              |
| len_eq, count_eq | length or count equals        | len(A) == B                  | 'abc' len_eq 3, [1,2] len_eq 2 |
| len_gt, count_gt | length greater than           | len(A) > B                   | 'abc' len_gt 2, [1,2,3] len_gt 2 |
| len_ge, count_ge | length greater than or equals | len(A) >= B                  | 'abc' len_ge 3, [1,2,3] len_ge 3 |
| len_lt, count_lt | length less than              | len(A) < B                   | 'abc' len_lt 4, [1,2,3] len_lt 4 |
| len_le, count_le | length less than or equals    | len(A) <= B                  | 'abc' len_le 3, [1,2,3] len_le 3 |
| contains        | contains                       | [1, 2] contains 1            | 'abc' contains 'a', [1,2,3] len_lt 4 |
| contained_by    | contained by                   | A in B                        | 'a' contained_by 'abc', 1 contained_by [1,2] |
| type_match      | A is instance of B             | isinstance(A, B)             | 123 type_match 'int'          |
| regex_match     | regex matches                  | re.match(B, A)               | 'abcdef' regex 'a|w+d'        |
| startswith      | starts with                    | A.startswith(B) is True       | 'abc' startswith 'ab'         |
| endswith        | ends with                      | A.endswith(B) is True         | 'abc' endswith 'bc'           |



## 小技巧
```
# 用例skip机制，支持用例层和API层
1. 无条件跳过：skip: skip this test unconditionally
2. 自定义函数返回True：skipIf: ${skip_test_in_production_env()}
3. 自定义函数返回False：skipUnless: ${skip_test_in_production_env()}

# 日志输出需要指定绝对路径或相对路径，不能指定单独一个文件名（文件可以未创建）
hrun --log-level debug --log-file ./test.log   api/youcloud/query_product_api.yml

响应体默认可引用属性变量：status_code, cookies, elapsed, headers, content, body, text, json, encoding, ok, reason, url
e.g.
"status_code"
"content"
"content.person.name.first_name"
"body"
"body.token"
"headers"
"headers.content-type"
"cookies"

$需要转义为：$$

自定义函数使用了字典参数，需要使用双引号包围，避免YAML解析器会将其误认为是字典定义。例如：
sign: "${get_sign_v3({device_sn: $device_sn, os_platform: $os_platform, app_version: $app_version})}"
```





## FQA
### 1、安装 apimeter 报错
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


### 2、命令 apimeter -V 报错
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


### 3、在APIMeter v2.7.1版本中调整为Python3.6+
实际使用过程中，都是python3的环境的。但如果有需要，调整Python版本号，依旧可以在2.7+环境中正常使用。