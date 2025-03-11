
在测试用例中，包含预期结果这么一项，用于辅助测试人员执行测试用例时判断系统的功能是否正常。而在自动化测试中，我们的目标是让测试用例自动执行，因此自动化测试用例中同样需要包含预期结果一项，只不过系统响应结果不再由人工来进行判断，而是交由测试工具或框架来实现。

这部分功能对应的就是测试结果校验器（validator），基本上能称得上自动化测试工具或框架的都包含该功能特性。

## 1、校验器支持两种格式
```
- {"check": check_item, "comparator": comparator_name, "expect": expect_value}  # 一般格式
- comparator_name: [check_item, expect_value]  # 简化格式
```

## 2、支持自定义校验器
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

## 3、支持在校验器中引用变量
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

## 4、支持正则表达式提取结果校验内容
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

## 5、附录：内置校验器
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
