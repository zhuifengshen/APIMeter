import unittest
from unittest.mock import Mock, patch, MagicMock

from apimeter import exceptions, validator, context, response


class TestValidator(unittest.TestCase):
    
    def setUp(self):
        """测试前置设置"""
        # 创建模拟的响应对象
        self.mock_resp = Mock()
        self.mock_resp.status_code = 200
        self.mock_resp.headers = {"Content-Type": "application/json"}
        self.mock_resp.cookies.get_dict.return_value = {"session_id": "test_session"}
        self.mock_resp.text = '{"success": true, "token": "abcd1234efgh5678", "user": {"id": 123, "name": "test"}}'
        self.mock_resp.json.return_value = {"success": True, "token": "abcd1234efgh5678", "user": {"id": 123, "name": "test"}}
        self.mock_resp.encoding = "utf-8"
        self.mock_resp.ok = True
        self.mock_resp.reason = "OK"
        self.mock_resp.url = "http://test.com/api/test"
        
        # 创建ResponseObject
        self.resp_obj = response.ResponseObject(self.mock_resp)
        
        # 创建模拟的session context
        self.session_context = Mock()
        self.session_context.test_variables_mapping = {
            "token": "abcd1234efgh5678",
            "user_id": 123,
            "expected_status": 200
        }
        self.session_context.eval_content = Mock(side_effect=lambda x: x)
        
        # 创建validator实例
        self.validator = validator.Validator(self.session_context, self.resp_obj)
    
    def test_validate_script_assert_success(self):
        """测试assert语句校验成功"""
        script = [
            "assert status_code == 200",
            "assert content.success is True",
            "assert len(content.token) == 16"
        ]
        
        result = self.validator.validate_script(script)
        
        self.assertEqual(result["check_result"], "pass")
        self.assertEqual(result["output"], "success")
        self.assertEqual(len(result["details"]), 3)
        
        # 检查每个校验项的结果
        for detail in result["details"]:
            self.assertEqual(detail["check_result"], "pass")
            self.assertEqual(detail["output"], "success")
    
    def test_validate_script_assert_failure(self):
        """测试assert语句校验失败"""
        script = [
            "assert status_code == 200",  # 成功
            "assert status_code == 404",  # 失败
            "assert content.success is True"  # 继续执行
        ]
        
        result = self.validator.validate_script(script)
        
        self.assertEqual(result["check_result"], "fail")
        self.assertEqual(result["output"], "script validation failed")
        self.assertEqual(len(result["details"]), 3)
        
        # 检查具体结果
        self.assertEqual(result["details"][0]["check_result"], "pass")
        self.assertEqual(result["details"][1]["check_result"], "fail")
        self.assertIn("AssertionError", result["details"][1]["output"])
        self.assertEqual(result["details"][2]["check_result"], "pass")
    
    def test_validate_script_name_error(self):
        """测试变量不存在的情况"""
        script = [
            "assert status_code == 200",
            "assert invalid_field == 'test'"  # 不存在的变量
        ]
        
        result = self.validator.validate_script(script)
        
        self.assertEqual(result["check_result"], "fail")
        self.assertEqual(len(result["details"]), 2)
        
        # 第一个成功，第二个失败
        self.assertEqual(result["details"][0]["check_result"], "pass")
        self.assertEqual(result["details"][1]["check_result"], "fail")
        self.assertIn("NameError", result["details"][1]["output"])
    
    def test_validate_script_syntax_error(self):
        """测试语法错误"""
        script = [
            "assert status_code == 200",
            "assert invalid syntax here"  # 语法错误
        ]
        
        result = self.validator.validate_script(script)
        
        self.assertEqual(result["check_result"], "fail")
        self.assertEqual(len(result["details"]), 2)
        
        # 第一个成功，第二个语法错误
        self.assertEqual(result["details"][0]["check_result"], "pass")
        self.assertEqual(result["details"][1]["check_result"], "fail")
        self.assertIn("SyntaxError", result["details"][1]["output"])
    
    def test_validate_script_custom_function_success(self):
        """测试自定义函数校验成功"""
        # 模拟eval_content解析函数调用
        def mock_eval_content(content):
            if content == "${validate_token($token)}":
                return True
            return content
        
        self.session_context.eval_content = mock_eval_content
        
        script = [
            "assert status_code == 200",
            "${validate_token($token)}"
        ]
        
        result = self.validator.validate_script(script)
        
        self.assertEqual(result["check_result"], "pass")
        self.assertEqual(len(result["details"]), 2)
        
        # 检查自定义函数调用结果
        self.assertEqual(result["details"][1]["check_result"], "pass")
        self.assertEqual(result["details"][1]["output"], "True")
    
    def test_validate_script_custom_function_failure(self):
        """测试自定义函数校验失败"""
        def mock_eval_content(content):
            if content == "${validate_data(content)}":
                raise ValueError("Validation failed")
            return content
        
        self.session_context.eval_content = mock_eval_content
        
        script = [
            "assert status_code == 200",
            "${validate_data(content)}"
        ]
        
        result = self.validator.validate_script(script)
        
        self.assertEqual(result["check_result"], "fail")
        self.assertEqual(len(result["details"]), 2)
        
        # 检查自定义函数异常处理
        self.assertEqual(result["details"][1]["check_result"], "fail")
        self.assertIn("ValueError", result["details"][1]["output"])
    
    def test_validate_script_mixed_scenarios(self):
        """测试混合场景：成功、失败、异常"""
        script = [
            "assert status_code == 200",           # 成功
            "assert content.success is True",      # 成功
            "assert status_code == 404",           # 失败
            "assert undefined_var == 'test'",      # 异常
            "assert len(content.token) == 16"      # 继续执行，成功
        ]
        
        result = self.validator.validate_script(script)
        
        self.assertEqual(result["check_result"], "fail")
        self.assertEqual(len(result["details"]), 5)
        
        # 检查每个校验项的结果
        expected_results = ["pass", "pass", "fail", "fail", "pass"]
        for i, expected in enumerate(expected_results):
            self.assertEqual(result["details"][i]["check_result"], expected)
    
    def test_validate_script_response_field_access(self):
        """测试响应字段访问"""
        script = [
            "assert headers['Content-Type'] == 'application/json'",
            "assert 'session_id' in cookies",
            "assert content.user.id == 123",
            "assert content.user.name == 'test'"
        ]
        
        result = self.validator.validate_script(script)
        
        self.assertEqual(result["check_result"], "pass")
        self.assertEqual(len(result["details"]), 4)
        
        # 所有校验都应该成功
        for detail in result["details"]:
            self.assertEqual(detail["check_result"], "pass")
    
    def test_validate_script_variable_reference(self):
        """测试变量引用"""
        script = [
            "assert status_code == $expected_status",
            "assert content.user.id == $user_id"
        ]
        
        # 模拟变量解析
        def mock_eval_content(content):
            if content == "assert status_code == $expected_status":
                return "assert status_code == 200"
            elif content == "assert content.user.id == $user_id":
                return "assert content.user.id == 123"
            return content
        
        self.session_context.eval_content = mock_eval_content
        
        result = self.validator.validate_script(script)
        
        self.assertEqual(result["check_result"], "pass")
        self.assertEqual(len(result["details"]), 2)
        
        # 所有校验都应该成功
        for detail in result["details"]:
            self.assertEqual(detail["check_result"], "pass")
    
    def test_validate_script_empty_list(self):
        """测试空校验脚本列表"""
        script = []
        
        result = self.validator.validate_script(script)
        
        self.assertEqual(result["check_result"], "pass")
        self.assertEqual(result["output"], "success")
        self.assertEqual(len(result["details"]), 0)
    
    def test_validate_script_complex_expressions(self):
        """测试复杂表达式"""
        script = [
            "assert status_code in [200, 201, 202]",
            "assert len(content.token) >= 16",
            "assert content.user.id > 0 and content.user.name is not None"
        ]
        
        result = self.validator.validate_script(script)
        
        self.assertEqual(result["check_result"], "pass")
        self.assertEqual(len(result["details"]), 3)
        
        # 所有校验都应该成功
        for detail in result["details"]:
            self.assertEqual(detail["check_result"], "pass")
    
    def test_validate_script_with_custom_error_messages(self):
        """测试带自定义错误消息的断言"""
        script = [
            "assert status_code == 200, f'Expected 200, got {status_code}'",
            "assert content.success is True, 'API call should succeed'"
        ]
        
        result = self.validator.validate_script(script)
        
        self.assertEqual(result["check_result"], "pass")
        self.assertEqual(len(result["details"]), 2)
        
        # 所有校验都应该成功
        for detail in result["details"]:
            self.assertEqual(detail["check_result"], "pass")
    
    def test_validate_script_result_format(self):
        """测试返回结果格式"""
        script = ["assert status_code == 200"]
        
        result = self.validator.validate_script(script)
        
        # 检查返回结果包含必要字段
        self.assertIn("validate_script", result)
        self.assertIn("check_result", result)
        self.assertIn("output", result)
        self.assertIn("details", result)
        
        # 检查details格式
        self.assertEqual(len(result["details"]), 1)
        detail = result["details"][0]
        self.assertIn("script", detail)
        self.assertIn("check_result", detail)
        self.assertIn("output", detail)
        
        # 检查脚本内容
        self.assertEqual(detail["script"], "assert status_code == 200")
    
    def test_eval_validator_check_params_error(self):
        """测试__eval_validator_check方法的ParamsError异常处理"""
        # 模拟extract_field抛出ParamsError
        self.resp_obj.extract_field = Mock(side_effect=exceptions.ParamsError("Field not found"))
        
        with self.assertRaises(exceptions.ParamsError):
            self.validator._Validator__eval_validator_check("invalid_field")
    
    def test_eval_validator_check_extract_failure(self):
        """测试__eval_validator_check方法的ExtractFailure异常处理"""
        # 模拟extract_field抛出ExtractFailure
        self.resp_obj.extract_field = Mock(side_effect=exceptions.ExtractFailure("Extract failed"))
        
        with self.assertRaises(exceptions.ExtractFailure):
            self.validator._Validator__eval_validator_check("invalid_field")
    
    def test_eval_validator_check_variable_not_found(self):
        """测试__eval_validator_check方法的VariableNotFound异常处理"""
        # 模拟eval_content抛出VariableNotFound
        self.session_context.eval_content = Mock(side_effect=exceptions.VariableNotFound("Variable not found"))
        
        with self.assertRaises(exceptions.VariableNotFound):
            self.validator._Validator__eval_validator_check({"test": "$undefined_var"})
    
    def test_eval_validator_check_other_exception(self):
        """测试__eval_validator_check方法的其他异常处理"""
        # 模拟其他类型异常
        self.resp_obj.extract_field = Mock(side_effect=ValueError("Some error"))
        
        result = self.validator._Validator__eval_validator_check("test_field")
        
        # 应该返回错误信息字符串
        self.assertEqual(result, "ValueError: Some error")
    
    def test_eval_validator_expect_params_error(self):
        """测试__eval_validator_expect方法的ParamsError异常处理"""
        # 模拟eval_content抛出ParamsError
        self.session_context.eval_content = Mock(side_effect=exceptions.ParamsError("Params error"))
        
        with self.assertRaises(exceptions.ParamsError):
            self.validator._Validator__eval_validator_expect("$invalid_var")
    
    def test_eval_validator_expect_other_exception(self):
        """测试__eval_validator_expect方法的其他异常处理"""
        # 模拟其他类型异常
        self.session_context.eval_content = Mock(side_effect=RuntimeError("Runtime error"))
        
        result = self.validator._Validator__eval_validator_expect("test_value")
        
        # 应该返回错误信息字符串
        self.assertEqual(result, "RuntimeError: Runtime error")
    
    def test_response_field_proxy_integration(self):
        """测试ResponseFieldProxy集成"""
        script = [
            "assert content.success is True",
            "assert content.user.id == 123",
            "assert headers['Content-Type'] == 'application/json'"
        ]
        
        result = self.validator.validate_script(script)
        
        self.assertEqual(result["check_result"], "pass")
        self.assertEqual(len(result["details"]), 3)
        
        # 所有校验都应该成功
        for detail in result["details"]:
            self.assertEqual(detail["check_result"], "pass")


if __name__ == '__main__':
    unittest.main()
