import multiprocessing
import time
import unittest

import requests

from tests.api_server import FLASK_APP_PORT, HTTPBIN_HOST, HTTPBIN_PORT
from tests.api_server import app as flask_app
from tests.api_server import gen_random_string, get_sign, httpbin_app


def run_flask():
    flask_app.run(port=FLASK_APP_PORT)


def run_httpbin():
    if httpbin_app:
        httpbin_app.run(host=HTTPBIN_HOST, port=HTTPBIN_PORT)


class ApiServerUnittest(unittest.TestCase):
    """Test case class that sets up an HTTP server which can be used within the tests"""

    @classmethod
    def setUpClass(cls):
        cls.host = "http://127.0.0.1:5000"
        cls.flask_process = multiprocessing.Process(target=run_flask)
        cls.httpbin_process = multiprocessing.Process(target=run_httpbin)
        cls.flask_process.start()
        cls.httpbin_process.start()                
        # Wait for servers to be ready with health check
        cls._wait_for_server_ready()
        cls.api_client = requests.Session()
    
    @classmethod
    def _wait_for_server_ready(cls, max_wait_time=30):
        """Wait for the Flask server to be ready with health check"""
        import time
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            try:
                # Try to connect to the Flask server
                response = requests.get(cls.host, timeout=3)
                if response.status_code == 200 and "Hello World!" in response.text:
                    # Server is ready and responding correctly
                    time.sleep(0.5)  # Give it a bit more time to be fully ready
                    return
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, requests.exceptions.RequestException):
                # Server not ready yet, wait a bit more
                pass
            
            time.sleep(0.5)
        
        # If we get here, server didn't start in time
        raise RuntimeError(f"Flask server failed to start within {max_wait_time} seconds on port {cls.flask_port}")


    @classmethod
    def tearDownClass(cls):
        cls.flask_process.terminate()
        cls.httpbin_process.terminate()

    def get_token(self, user_agent, device_sn, os_platform, app_version):
        url = "%s/api/get-token" % self.host
        headers = {
            "Content-Type": "application/json",
            "User-Agent": user_agent,
            "device_sn": device_sn,
            "os_platform": os_platform,
            "app_version": app_version,
        }
        data = {"sign": get_sign(device_sn, os_platform, app_version)}

        resp = self.api_client.post(url, json=data, headers=headers)
        resp_json = resp.json()
        self.assertTrue(resp_json["success"])
        self.assertIn("token", resp_json)
        self.assertEqual(len(resp_json["token"]), 16)
        return resp_json["token"]

    def get_authenticated_headers(self):
        user_agent = "iOS/10.3"
        device_sn = gen_random_string(15)
        os_platform = "ios"
        app_version = "2.8.6"

        token = self.get_token(user_agent, device_sn, os_platform, app_version)
        headers = {"device_sn": device_sn, "token": token}
        return headers
