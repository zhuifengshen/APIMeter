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
- 3、之所以不写字HttpRunner，因为部分项目在debugtalk.py中导入了HttpRunner包并使用其已封装好的函数；


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

