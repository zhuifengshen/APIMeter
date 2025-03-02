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


## Development
```python
poetry install  # 拉取代码后安装依赖
poetry run python -m apimeter /path/to/api  # 完整生成报告
poetry run python -m apimeter /path/to/api --skip-success  # 报告忽略成功用例数据
poetry build  # 打包
poetry publish  # 发布，根据提示输入pypi账号密码
pip install -i https://pypi.Python.org/simple/ apimeter  # 指定安装源，因为刚发布其他平台未及时同步


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


## FQA
1、安装 apimeter 报错
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
