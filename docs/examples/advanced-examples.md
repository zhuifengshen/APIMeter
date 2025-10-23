# 高级用法示例

本文档提供 ApiMeter 高级特性的完整实战案例，涵盖真实业务场景中的最佳实践。

## 📚 示例目录

1. [电商 API 完整测试流程](#示例1电商-api-完整测试流程)
2. [OAuth2.0 认证流程测试](#示例2oauth20-认证流程测试)
3. [批量数据校验场景](#示例3批量数据校验场景)
4. [复杂签名生成与校验](#示例4复杂签名生成与校验)
5. [条件校验与业务逻辑](#示例5条件校验与业务逻辑)
6. [性能监控与告警](#示例6性能监控与告警)
7. [多环境配置管理](#示例7多环境配置管理)

## 示例1：电商 API 完整测试流程

### 场景描述

测试一个完整的电商下单流程，包括：
1. 用户登录获取 token
2. 查询商品列表
3. 将商品加入购物车
4. 创建订单
5. 支付订单
6. 查询订单状态

### 项目结构

```
ecommerce_test/
├── api/
│   ├── auth.yml          # 认证相关接口
│   ├── products.yml      # 商品相关接口
│   ├── cart.yml          # 购物车接口
│   └── orders.yml        # 订单接口
├── testcases/
│   └── test_order_flow.yml
├── debugtalk.py
└── .env
```

### debugtalk.py

```python
import hashlib
import hmac
import time
from apimeter.logger import log_info

SECRET_KEY = "ecommerce_secret"

def generate_order_sign(order_data):
    """生成订单签名"""
    sorted_keys = sorted(order_data.keys())
    sign_str = '&'.join([f"{k}={order_data[k]}" for k in sorted_keys])
    return hashlib.md5(sign_str.encode()).hexdigest()

def validate_product_list(products, min_count=1):
    """校验商品列表数据"""
    assert len(products) >= min_count, f"商品数量不足: {len(products)}"
    
    for product in products:
        # 必填字段检查
        assert product.get("id") is not None, "商品ID不能为空"
        assert product.get("name") is not None, "商品名称不能为空"
        assert product.get("price") is not None, "商品价格不能为空"
        
        # 价格合理性检查
        price = product.get("price", 0)
        assert price > 0, f"商品价格必须大于0: {price}"
        assert price < 1000000, f"商品价格异常过高: {price}"
        
        # 库存检查
        stock = product.get("stock", 0)
        assert stock >= 0, f"商品库存不能为负: {stock}"
    
    log_info(f"✓ 商品列表校验通过，共 {len(products)} 个商品")
    return True

def validate_order_data(order):
    """校验订单数据完整性"""
    required_fields = ["order_id", "user_id", "amount", "status", "items"]
    
    for field in required_fields:
        assert field in order, f"订单缺少必填字段: {field}"
    
    # 订单金额检查
    assert order["amount"] > 0, "订单金额必须大于0"
    
    # 订单商品检查
    assert len(order["items"]) > 0, "订单商品列表不能为空"
    
    # 状态检查
    valid_status = ["pending", "paid", "processing", "completed", "cancelled"]
    assert order["status"] in valid_status, f"订单状态无效: {order['status']}"
    
    return True
```

### 测试用例: testcases/test_order_flow.yml

```yaml
config:
  name: "电商下单完整流程测试"
  variables:
    base_url: "https://api.ecommerce.com"
    username: "test_user@example.com"
    password: "Test123456"
  
teststeps:
# ========== Step 1: 用户登录 ==========
- name: 用户登录获取token
  request:
    url: $base_url/api/v1/auth/login
    method: POST
    json:
      username: $username
      password: $password
  
  extract:
    - access_token: content.data.access_token
    - user_id: content.data.user_id
  
  script:
    - assert status_code == 200
    - assert content.success is True
    - assert content.data.access_token is not None
    - assert len(content.data.access_token) > 0
    - assert content.data.user_id > 0
    - assert elapsed.total_seconds < 2.0, "登录接口响应过慢"

# ========== Step 2: 查询商品列表 ==========
- name: 查询商品列表
  request:
    url: $base_url/api/v1/products
    method: GET
    headers:
      Authorization: "Bearer $access_token"
    params:
      category: "electronics"
      page: 1
      page_size: 20
  
  extract:
    - products: content.data.products
    - first_product_id: content.data.products[0].id
    - first_product_price: content.data.products[0].price
  
  script:
    # 基础校验
    - assert status_code == 200
    - assert content.success is True
    - assert len(content.data.products) > 0
    
    # 使用自定义函数校验商品列表
    - ${validate_product_list(content.data.products, 5)}
    
    # 批量校验所有商品的必填字段
    - |
      for product in content.data.products:
          assert product.get("id") is not None
          assert product.get("name") is not None
          assert product.get("price") > 0
          assert product.get("stock") >= 0

# ========== Step 3: 加入购物车 ==========
- name: 将商品加入购物车
  request:
    url: $base_url/api/v1/cart/add
    method: POST
    headers:
      Authorization: "Bearer $access_token"
    json:
      product_id: $first_product_id
      quantity: 2
  
  extract:
    - cart_item_id: content.data.cart_item_id
  
  script:
    - assert status_code == 200
    - assert content.success is True
    - assert content.data.cart_item_id is not None

# ========== Step 4: 创建订单 ==========
- name: 创建订单
  request:
    url: $base_url/api/v1/orders/create
    method: POST
    headers:
      Authorization: "Bearer $access_token"
    json:
      items:
        - product_id: $first_product_id
          quantity: 2
          price: $first_product_price
      shipping_address:
        province: "广东省"
        city: "深圳市"
        district: "南山区"
        detail: "科技园南区"
      remark: "请尽快发货"
  
  extract:
    - order_id: content.data.order_id
    - order_no: content.data.order_no
    - order_amount: content.data.amount
  
  script:
    # 状态码校验
    - assert status_code == 200
    - assert content.success is True
    
    # 订单基本信息校验
    - assert content.data.order_id > 0
    - assert content.data.order_no is not None
    - assert len(content.data.order_no) > 0
    
    # 使用自定义函数校验订单数据
    - ${validate_order_data(content.data)}
    
    # 订单金额校验
    - |
      expected_amount = $first_product_price * 2
      actual_amount = content.data.amount
      assert actual_amount == expected_amount, \
        f"订单金额不符: 期望{expected_amount}, 实际{actual_amount}"

# ========== Step 5: 支付订单 ==========
- name: 支付订单
  request:
    url: $base_url/api/v1/orders/$order_id/pay
    method: POST
    headers:
      Authorization: "Bearer $access_token"
    json:
      order_id: $order_id
      payment_method: "alipay"
      amount: $order_amount
  
  script:
    - assert status_code == 200
    - assert content.success is True
    - assert content.data.payment_status == "success"
    - assert content.data.order_status == "paid"

# ========== Step 6: 查询订单状态 ==========
- name: 查询订单状态
  request:
    url: $base_url/api/v1/orders/$order_id
    method: GET
    headers:
      Authorization: "Bearer $access_token"
  
  script:
    - assert status_code == 200
    - assert content.success is True
    - assert content.data.order_id == $order_id
    - assert content.data.status in ["paid", "processing"]
    - assert content.data.payment_status == "success"
    
    # 订单历史记录检查
    - |
      history = content.data.history
      assert len(history) > 0, "订单历史记录不能为空"
      
      # 检查是否包含创建和支付记录
      status_list = [h["status"] for h in history]
      assert "pending" in status_list, "缺少订单创建记录"
      assert "paid" in status_list, "缺少支付记录"
```

---

## 示例2：OAuth2.0 认证流程测试

### 完整 OAuth2 授权码模式

```yaml
config:
  name: "OAuth2.0 授权码流程测试"
  variables:
    auth_server: "https://auth.example.com"
    api_server: "https://api.example.com"
    client_id: "test_client_id"
    client_secret: "test_client_secret"
    redirect_uri: "https://example.com/callback"

teststeps:
# Step 1: 获取授权码
- name: 获取授权码
  request:
    url: $auth_server/oauth/authorize
    method: POST
    json:
      client_id: $client_id
      response_type: "code"
      redirect_uri: $redirect_uri
      scope: "read write"
      state: "random_state_123"
  
  extract:
    - auth_code: content.code
  
  script:
    - assert status_code == 200
    - assert content.code is not None
    - assert len(content.code) > 0

# Step 2: 用授权码换取访问令牌
- name: 获取访问令牌
  request:
    url: $auth_server/oauth/token
    method: POST
    json:
      client_id: $client_id
      client_secret: $client_secret
      code: $auth_code
      grant_type: "authorization_code"
      redirect_uri: $redirect_uri
  
  extract:
    - access_token: content.access_token
    - refresh_token: content.refresh_token
    - expires_in: content.expires_in
  
  script:
    - assert status_code == 200
    - assert content.access_token is not None
    - assert content.refresh_token is not None
    - assert content.token_type == "Bearer"
    - assert content.expires_in > 0
    - assert isinstance(content.expires_in, int)

# Step 3: 使用访问令牌请求API
- name: 使用访问令牌获取用户信息
  request:
    url: $api_server/api/user/profile
    method: GET
    headers:
      Authorization: "Bearer $access_token"
  
  script:
    - assert status_code == 200
    - assert content.user_id is not None
    - assert content.username is not None

# Step 4: 刷新令牌
- name: 使用刷新令牌获取新的访问令牌
  request:
    url: $auth_server/oauth/token
    method: POST
    json:
      client_id: $client_id
      client_secret: $client_secret
      refresh_token: $refresh_token
      grant_type: "refresh_token"
  
  extract:
    - new_access_token: content.access_token
  
  script:
    - assert status_code == 200
    - assert content.access_token is not None
    - assert content.access_token != "$access_token"
```

---

## 示例3：批量数据校验场景

使用 ApiMeter 的通配符和自定义函数进行高效的批量数据校验。

```yaml
config:
  name: "批量数据校验示例"
  base_url: "https://api.example.com"

teststeps:
- name: 获取商品数据（包含多层嵌套）
  request:
    url: $base_url/api/products/detail
    method: GET
    params:
      id: 12345
  
  script:
    # 使用通配符批量校验所有 SKU 字段
    - ${check(content,
        data.product.purchasePlan.*.sku.*.id,
        data.product.purchasePlan.*.sku.*.amount,
        data.product.purchasePlan.*.sku.*.currency,
        data.product.purchasePlan.*.sku.*.duration
      )}
    
    # 正则和类型校验
    - ${check(content,
        '_url ~= ^https?://.*',
        'data.product @= dict',
        'data.product.purchasePlan @= list',
        'data.default_currency =* [USD, CNY, EUR]'
      )}
    
    # 自定义复杂校验
    - |
      plans = content.data.product.purchasePlan
      for plan in plans:
          assert plan.get("plan_id") is not None
          assert len(plan.get("sku", [])) > 0
          
          for sku in plan["sku"]:
              # 金额合理性检查
              amount = sku.get("amount", 0)
              origin = sku.get("origin_amount", 0)
              assert amount > 0, f"SKU金额必须大于0: {amount}"
              assert origin >= amount, f"原价不能低于现价: {origin} < {amount}"
              
              # 折扣计算
              if origin > 0:
                  discount = amount / origin
                  assert 0 < discount <= 1, f"折扣率异常: {discount}"
```

---

## 示例4：复杂签名生成与校验

实际项目中常见的签名场景。

### debugtalk.py

```python
import hashlib
import hmac
import time
import json

def generate_api_signature(params_dict):
    """
    生成API签名
    
    规则：
    1. 按参数名ASCII码排序
    2. 拼接为 key1=value1&key2=value2 格式
    3. 附加密钥
    4. MD5加密
    """
    secret_key = params_dict.pop("_secret", "default_secret")
    
    # 过滤空值和签名字段
    filtered = {k: v for k, v in params_dict.items() 
                if v is not None and k != 'sign'}
    
    # 排序
    sorted_params = sorted(filtered.items())
    
    # 拼接
    sign_str = '&'.join([f"{k}={v}" for k, v in sorted_params])
    sign_str += f"&key={secret_key}"
    
    # MD5
    return hashlib.md5(sign_str.encode('utf-8')).hexdigest().upper()
```

### 测试用例

```yaml
variables:
  app_key: "my_app_key"
  app_secret: "my_app_secret"
  timestamp: ${get_timestamp()}

teststeps:
- name: 带签名的API请求
  request:
    url: $base_url/api/secure/data
    method: POST
    json:
      app_key: $app_key
      timestamp: $timestamp
      nonce: ${gen_random_string(16)}
      data:
        user_id: 12345
        action: "query"
      sign: "${generate_api_signature({
        app_key: $app_key,
        timestamp: $timestamp,
        nonce: ${gen_random_string(16)},
        data: {user_id: 12345, action: 'query'},
        _secret: $app_secret
      })}"
  
  script:
    - assert status_code == 200
    - assert content.success is True
```

---

## 示例5：条件校验与业务逻辑

根据不同的业务状态进行不同的校验。

```yaml
script:
  # 根据用户类型进行不同校验
  - |
    user_type = content.user.type
    
    if user_type == "vip":
        # VIP 用户校验
        assert content.user.vip_level > 0, "VIP等级必须大于0"
        assert content.user.vip_expires is not None, "VIP到期时间不能为空"
        assert content.user.discount >= 0.7, f"VIP折扣率异常: {content.user.discount}"
        assert len(content.user.privileges) > 0, "VIP特权列表不能为空"
    
    elif user_type == "premium":
        # 高级用户校验
        assert content.user.premium_features is not None
        assert len(content.user.premium_features) >= 3, "高级功能至少3项"
        assert content.user.ad_free is True, "高级用户应该无广告"
    
    elif user_type == "free":
        # 免费用户校验
        assert content.user.ads_enabled is True, "免费用户应该显示广告"
        assert content.user.daily_limit is not None, "每日限额必须设置"
    
    else:
        raise ValueError(f"未知用户类型: {user_type}")
  
  # 根据订单状态进行不同校验
  - |
    order_status = content.order.status
    
    if order_status == "pending":
        assert content.order.payment_url is not None, "待支付订单必须有支付链接"
        assert content.order.expire_time is not None, "待支付订单必须有过期时间"
    
    elif order_status == "paid":
        assert content.order.payment_time is not None, "已支付订单必须有支付时间"
        assert content.order.transaction_id is not None, "已支付订单必须有交易号"
    
    elif order_status == "cancelled":
        assert content.order.cancel_reason is not None, "取消订单必须有取消原因"
        assert content.order.refund_status is not None, "取消订单必须有退款状态"
```

---

## 示例6：性能监控与告警

在功能测试的同时监控性能指标。

```yaml
script:
  # 性能监控
  - |
    response_time = elapsed.total_seconds
    api_path = url.split('?')[0]  # 去除查询参数
    
    # 定义不同接口的性能标准
    performance_standards = {
        "/api/users": 0.5,           # 用户接口：500ms
        "/api/products": 1.0,        # 商品接口：1s
        "/api/search": 2.0,          # 搜索接口：2s
        "/api/reports": 5.0,         # 报表接口：5s
    }
    
    # 查找匹配的性能标准
    max_time = 1.0  # 默认标准
    for path, limit in performance_standards.items():
        if path in api_path:
            max_time = limit
            break
    
    # 性能告警
    if response_time > max_time:
        print(f"⚠️  性能告警: {api_path}")
        print(f"   响应时间: {response_time:.3f}s")
        print(f"   性能标准: {max_time}s")
        print(f"   超出: {(response_time - max_time):.3f}s")
    
    # 严重超时断言
    assert response_time < max_time * 2, \
        f"严重超时: {response_time:.3f}s (标准: {max_time}s)"
  
  # 数据量监控
  - |
    if hasattr(content, 'data') and isinstance(content.data, list):
        data_count = len(content.data)
        
        # 数据量告警
        if data_count > 1000:
            print(f"⚠️  数据量告警: 返回{data_count}条数据")
            print(f"   建议：考虑分页或限制返回数量")
        
        # 数据量断言
        assert data_count <= 5000, f"数据量过大: {data_count}条"
```

---

## 示例7：多环境配置管理

### .env 文件管理

**.env.dev**（开发环境）:
```bash
ENV=development
BASE_URL=https://dev-api.example.com
APP_KEY=dev_app_key
APP_SECRET=dev_secret
DB_HOST=dev-db.example.com
TIMEOUT=10
```

**.env.test**（测试环境）:
```bash
ENV=testing
BASE_URL=https://test-api.example.com
APP_KEY=test_app_key
APP_SECRET=test_secret
DB_HOST=test-db.example.com
TIMEOUT=30
```

**.env.prod**（生产环境）:
```bash
ENV=production
BASE_URL=https://api.example.com
APP_KEY=prod_app_key
APP_SECRET=prod_secret
DB_HOST=prod-db.example.com
TIMEOUT=60
```

### 测试用例

```yaml
config:
  name: "多环境测试用例"
  variables:
    env: ${ENV(ENV)}
    base_url: ${ENV(BASE_URL)}
    app_key: ${ENV(APP_KEY)}
    app_secret: ${ENV(APP_SECRET)}
    timeout: ${ENV(TIMEOUT)}

teststeps:
- name: 环境检查
  request:
    url: $base_url/api/health
    method: GET
  
  script:
    - assert status_code == 200
    - |
      # 根据环境进行不同的校验
      env = "$env"
      
      if env == "development":
          # 开发环境：可能返回调试信息
          print("开发环境测试")
      elif env == "testing":
          # 测试环境：标准校验
          assert content.environment == "testing"
      elif env == "production":
          # 生产环境：严格校验
          assert content.environment == "production"
          assert "debug" not in content  # 生产环境不应有调试信息
```

### 运行不同环境

```bash
# 开发环境
export $(cat .env.dev | xargs) && hrun testcases/

# 测试环境
export $(cat .env.test | xargs) && hrun testcases/

# 生产环境
export $(cat .env.prod | xargs) && hrun testcases/ --skip-success
```

---

## 📝 总结

这些示例展示了 ApiMeter 在实际项目中的应用：

| 场景 | 核心特性 | 价值 |
|-----|---------|------|
| 电商流程 | script + 自定义函数 | 完整业务流程测试 |
| OAuth2 | 变量提取 + 链式调用 | 复杂认证流程 |
| 批量校验 | 通配符 + 正则 | 高效数据校验 |
| 签名校验 | 字典参数 + 函数 | 安全接口测试 |
| 条件校验 | 多行脚本 + 业务逻辑 | 灵活的校验策略 |
| 性能监控 | elapsed + 条件判断 | 功能+性能结合 |
| 多环境 | 环境变量 + 配置管理 | 环境隔离 |

**更多学习资源：**
- [10分钟快速上手](../quickstart.md)
- [自定义脚本校验](../prepare/script.md)
- [自定义函数高级用法](../features/advanced-functions.md)
- [全局变量完整指南](../features/global-variables.md)

---

**有问题？** 查看 [FAQ](../FAQ.md) 或 [提交 Issue](https://git.umlife.net/utils/apimeter/issues)

