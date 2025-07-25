# YAML 用例语法格式注意事项

APIMeter测试用例格式是基于YAML，YAML本身有自己语法要求，加上测试用例中包含自定义变量、全局变量转义、自定义函数、列表参数、对象参数、复杂嵌套对象参数、链式参数、正则参数等内容，写测试用例有时会遇到用例文件解析失败的语法问题，因此梳理一下常见的错误写法格式，汇总为一份YAML用例语法格式注意事项文档，方便大家避坑和排查问题。

## 一、YAML语法排查

### 1、IDE内置YAML语法高亮
如果用例存在语法高亮异常不规则，则说明存在YAML语法问题，需要纠正

### 2、内置命令，一键排查
```shell
# Validate YAML/JSON api/testcase/testsuite format.
apimeter --validate [VALIDATE ...]

# Example: testcase file
apimeter --validate api/youcloud/account/query_areaCodeList_api.yml

# Example: testcase folder
apimeter --validate api/youcloud/account
```


## 二、常见错误概览

| 错误信息 | 可能原因 | 解决方案 |
|---------|---------|---------|
| `mapping values are not allowed here` | 函数参数中的`{}`被误认为字典 | 用引号包围整个函数调用 |
| `while parsing a flow sequence` | 列表语法中特殊字符未处理 | 使用多行格式或加引号 |
| `found undefined tag handle` | 变量引用格式错误 | 检查`${}`格式和变量名 |
| `VariableNotFound、FunctionNotFound` | 变量、函数未定义或引用错误 | 检查变量、函数定义和引用语法 |


## 三、常见问题示例

### 1、校验器错误写法 ❌
```yaml
validate:
  - eq: [${validate_token($token)}, true]  # YAML的列表（数组）包含特殊字符的函数调用时，会导致语法错误
```

#### 报错信息
```shell
ERROR    while parsing a flow sequence
expected ',' or ']', but got '{'
```

#### ✅ 正确写法1：单行格式（加引号）
```yaml
validate:
  - eq: ["${validate_token($token)}", true]
```

#### ✅ 正确写法2：多行格式（推荐）

```yaml
validate:
  - eq: 
    - ${validate_token($token)}
    - true
```

### 2、字典参数错误写法 ❌
```yaml
sign: ${get_sign_v3({device_sn: $device_sn, os_platform: $os_platform})} # 函数参数包含花括号 `{}` 时，YAML解析器会将其误认为是字典定义，导致语法错误
```

#### 报错信息
```shell
ERROR    mapping values are not allowed here
```

#### ✅ 正确写法1：使用双引号和转义
```yaml
sign: "${get_sign_v3({\"device_sn\": $device_sn, \"os_platform\": $os_platform})}"
```

#### ✅ 正确写法2：使用双引号+单引号
```yaml
sign: "${get_sign_v3({'device_sn': $device_sn, 'os_platform': $os_platform})}"
```

#### ✅ 正确写法3：使用双引号
```yaml
sign: "${get_sign_v3({device_sn: $device_sn, os_platform: $os_platform})}" # YAML原生字典语法（推荐）
```


## 四、YAML用例正确语法姿势

### 1、各种函数调用的正确写法
```yaml
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

### 2、包含列表参数的函数调用的正确写法
```yaml
sign: ${get_sign($device_sn, $os_platform, $app_version)}
sign: "${get_sign_v2([$device_sn, $os_platform, $app_version])}"
sign: ${get_sign_v2([$device_sn, $os_platform, $app_version])}
```

### 3、全局变量正确用法

#### APIMeter提供以下内置全局变量，无需使用`$`前缀
```yaml
# 内置全局变量列表
- content / body / text / json    # 响应体数据
- status_code                     # HTTP状态码
- headers                         # 响应头
- cookies                         # Cookie信息
- elapsed                         # 请求耗时
- encoding / ok / reason / url    # 其他响应信息
```

##### ✅ **正确使用方式**
```yaml
# 直接使用全局变量
validate:
  - eq: [status_code, 200]
  - eq: [content.token, $expected_token]
  - eq: [headers.content-type, "application/json"]
# 在函数中引用全局变量
script:
  - ${validate_response(content)}
  - ${check_headers(headers)}
```

##### ❌ **错误写法**
```yaml
# 全局变量前加$符号
validate:
  - eq: [$status_code, 200]        # 错误！
  - eq: [$content.token, "abc"]    # 错误！
```

#### 当数据字段与全局变量同名时，使用反斜杠`\`转义

##### ✅ **正确使用转义**

```yaml
# 当响应数据中有名为"content"的字段时
validate:
  - eq:
    - ${check_data_not_null(content.data.lines, \content)}  # \content 表示字符串 "content"
    - True

# 支持转义所有全局变量
script:
  - ${validate_field_name(\status_code, \headers, \content)}
```

##### ❌ **错误写法**

```yaml
# 直接使用会被解析为全局变量而非字面量
validate:
  - eq:
    - ${check_field_name(content.data, content)}  # content被解析为全局变量值
    - True
```


### 4、引号正确使用规则

#### **何时必须使用引号**

1. **包含花括号`{}`的函数调用**
2. **包含方括号`[]`的函数调用**  
3. **单行列表格式中的复杂表达式**
4. **包含冒号`:`的字符串值**

#### ✅ **正确示例**

```yaml
# 字典参数必须加引号
sign: "${get_sign({device: $device_sn})}"

# 包含冒号的值必须加引号
url: "http://example.com:8080/api"

# 单行校验器必须加引号
validate:
  - eq: ["${complex_func($param)}", "expected"]

# 列表参数建议加引号
data: "${process_list([$item1, $item2])}"  
```

#### ❌ **错误示例**

```yaml
# 字典参数无引号 - 解析错误
sign: ${get_sign({device: $device_sn})}

# 单行校验器无引号 - 解析错误  
validate:
  - eq: [${func($param)}, "expected"]
```


## 五、最佳实践
1. **检验器优先使用多行格式**：更清晰，不容易出错
2. **复杂参数统一加引号**：包含 `{}[]` 等特殊字符时
3. **保持团队脚本风格一致**：在同一个项目中使用统一的风格
4. **及时测试验证语法**：修改YAML后及时验证语法正确性
5. **最后提醒**：遇到语法错误时，首先检查引号使用和格式规范，90%的问题都能快速解决！ 🎯 


## 🔧 附录：测试用例模板

```yaml
teststeps:
-   name: "基础用例模板"
    variables:
        expected_status: 200
        expected_field: "success"

    request:
        url: "/api/endpoint"
        method: GET
        headers:
        Authorization: "Bearer ${get_auth_token($user_id)}"

    validate:
        - eq: [status_code, $expected_status]
        - eq: [content.status, $expected_field]
        - eq:
        - "${validate_response_format(content)}"
        - True

    script:
        - assert status_code == 200
        - assert content.success is True
        - ${log_response_time(elapsed.total_seconds)}
```