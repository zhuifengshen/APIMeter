
# ApiMeter

*ApiMeter* is a simple & elegant, yet powerful HTTP(S) testing framework. Enjoy! ✨ 🚀 ✨

## Design Philosophy

- Embrace open source, stand on giants' shoulders, like [`Requests`][Requests], [`unittest`][unittest] and [`Locust`][Locust].
- Convention over configuration.
- Pursuit of high rewards, write once and achieve a variety of testing needs

## Key Features

- Inherit all powerful features of [`Requests`][Requests], just have fun to handle HTTP(S) in human way.
- Define testcases in YAML or JSON format in concise and elegant manner.
- Record and generate testcases with [`HAR`][HAR] support. see [`har2case`][har2case].
- Supports `variables`/`extract`/`validate` mechanisms to create full test scenarios.
- Supports perfect hook mechanism.
- With `debugtalk.py` plugin, very easy to implement complex logic in testcase.
- Testcases can be run in diverse ways, with single testcase, multiple testcases, or entire project folder.
- Test report is concise and clear, with detailed log records.
- With reuse of [`Locust`][Locust], you can run performance test without extra work.
- CLI command supported, perfect combination with `CI/CD`.

## Documentation

ApiMeter is rich documented.

- [`中文用户使用手册`][user-docs-zh]
- [`开发历程记录博客`][development-blogs]
- [CHANGELOG](docs/CHANGELOG.md)

## Usage
```python
# 报告支持忽略成功用例数据
apimeter xxx.yml --skip-success


```


[Requests]: http://docs.python-requests.org/en/master/
[unittest]: https://docs.python.org/3/library/unittest.html
[Locust]: http://locust.io/
[har2case]: https://github.com/httprunner/har2case
[user-docs-zh]: http://docs.httprunner.org/
[development-blogs]: http://debugtalk.com/tags/httprunner/
[HAR]: http://httparchive.org/
[Swagger]: https://swagger.io/

