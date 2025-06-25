# ApiMeter

*ApiMeter* is a simple & elegant, yet powerful HTTP(S) API testing framework, base on HttpRunner v2.5.9. Enjoy! ✨ 🚀 ✨

## Document

1. ApiMeter 用户使用文档：[https://utils.git.umlife.net/apimeter](https://utils.git.umlife.net/apimeter/)
2. ApiMeter PYPI发布版本：[https://pypi.org/project/apimeter](https://pypi.org/project/apimeter)

## Usage
```python
pip install apimeter  # 安装，安装后可用内置命令：apimeter、hrun、apilocust
apimeter /path/to/api  # 完整生成报告
apimeter /path/to/api --skip-success  # 报告忽略成功用例数
```


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
python -m unittest tests.test_api.TestHttpRunner.test_validate_response_content # 运行单个测试用例

python -m tests.api_server 或 PYTHONPATH=. python tests/api_server.py # 启动测试示例服务器
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


# 逐行代码运行时内存分析
poetry shell
pip install memory-profiler
# 1. 导入方式
python -m apimeter ~/Project/ATDD/tmp/demo_api/ --skip-success
# 2. 装饰器方式
python -m memory_profiler apimeter ~/Project/ATDD/tmp/demo_api --skip-success --log-level error
# 3. 命令方式
mprof run apimeter /path/to/api
mprof plot  # 生成内存趋势图，安装依赖pip install matplotlib
# 参考链接：https://www.cnblogs.com/rgcLOVEyaya/p/RGC_LOVE_YAYA_603days_1.html
```

## Validate

### 1、校验器支持两种格式
```yaml
- {"check": check_item, "comparator": comparator_name, "expect": expect_value}  # 一般格式
- comparator_name: [check_item, expect_value]  # 简化格式
```

### 2、支持自定义校验器
对于自定义的校验函数，需要遵循三个规则：
- (1)自定义校验函数需放置到debugtalk.py中;
- (2)参数有两个：第一个为原始数据，第二个为原始数据经过运算后得到的预期结果值;
- (3)在校验函数中通过assert将实际运算结果与预期结果值进行比较;
```yaml
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
```yaml
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
```yaml
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
```yaml
- test:
    name: get token
    request:
        url: http://127.0.0.1:5000/api/get-token
        method: GET
    validate:
        - {"check": "LB123(.*)RB789", "comparator": "eq", "expect": "abc"}
```

### 5、内置全局变量
```yaml
content, body, text, json, status_code, cookies, elapsed, headers, encoding, ok, reason, url
```

用例模板中直接使用，无效使用前缀：$，例如：
"status_code"
"content"
"content.person.name.first_name"
"body"
"body.token"
"headers"
"headers.content-type"
"cookies"

### 5、内置校验器
| Comparator       | Description                    | A(check), B(expect)          | Examples                                     |
|------------------|--------------------------------|------------------------------|----------------------------------------------|
| eq               | value is equal                 | A == B                       | 9 eq 9                                       |
| lt               | less than                      | A < B                        | 7 lt 8                                       |
| le               | less than or equals            | A <= B                       | 7 le 8, 8 le 8                               |
| gt               | greater than                   | A > B                        | 8 gt 7                                       |
| ge               | greater than or equals         | A >= B                       | 8 ge 7, 8 ge 8                               |
| ne               | not equals                     | A != B                       | 6 ne 9                                       |
| str_eq           | string equals                  | str(A) == str(B)             | 123 str_eq '123'                             |
| len_eq, count_eq | length or count equals         | len(A) == B                  | 'abc' len_eq 3, [1,2] len_eq 2               |
| len_gt, count_gt | length greater than            | len(A) > B                   | 'abc' len_gt 2, [1,2,3] len_gt 2             |
| len_ge, count_ge | length greater than or equals  | len(A) >= B                  | 'abc' len_ge 3, [1,2,3] len_ge 3             |
| len_lt, count_lt | length less than               | len(A) < B                   | 'abc' len_lt 4, [1,2,3] len_lt 4             |
| len_le, count_le | length less than or equals     | len(A) <= B                  | 'abc' len_le 3, [1,2,3] len_le 3             |
| contains         | contains                       | [1, 2] contains 1            | 'abc' contains 'a', [1,2,3] len_lt 4         |
| contained_by     | contained by                   | A in B                       | 'a' contained_by 'abc', 1 contained_by [1,2] |
| type_match       | A is instance of B             | isinstance(A, B)             | 123 type_match 'int'                         |
| regex_match      | regex matches                  | re.match(B, A)               | 'abcdef' regex 'a|w+d'                       |
| startswith       | starts with                    | A.startswith(B) is True      | 'abc' startswith 'ab'                        |
| endswith         | ends with                      | A.endswith(B) is True        | 'abc' endswith 'bc'                          |



## 注意事项
```yaml
# 用例skip机制，支持用例层和API层
1. 无条件跳过：skip: skip this test unconditionally
2. 自定义函数返回True：skipIf: ${skip_test_in_production_env()}
3. 自定义函数返回False：skipUnless: ${skip_test_in_production_env()}

# 日志输出需要指定绝对路径或相对路径，不能指定单独一个文件名（文件可以未创建）
hrun --log-level debug --log-file ./test.log   api/youcloud/query_product_api.yml

# 自定义函数使用了字典参数，需要使用双引号包围，避免YAML解析器会将其误认为是字典定义。例如：
sign: "${get_sign_v3({device_sn: $device_sn, os_platform: $os_platform, app_version: $app_version})}"

# $转义
$$

# 一键打包发布，更多内容参考 scripts
make release-patch  MESSAGE="支持自动化打包发布，发布版本v2.8.4" # 自动累积小版本
make quick-release VERSION=2.85 MESSAGE="完善使用说明文档，发布版本v2.8.5" # 跳过单元测试
```

## 附录-相关链接
- HttpRunner: https://github.com/httprunner/
- Requests: http://docs.python-requests.org/en/master/
- unittest: https://docs.python.org/3/library/unittest.html
- Locust: http://locust.io/
- har2case: https://github.com/httprunner/har2case
- HAR: http://httparchive.org/
- Swagger: https://swagger.io/