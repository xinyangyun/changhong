# Python Project

一个最小可运行的 Python 项目。

## 运行

```bash
PYTHONPATH=src python3 -m python_project
```

默认会启动 Python 后端服务：

- 健康检查：`http://127.0.0.1:8000/api/health`
- 板块资金流：`http://127.0.0.1:8000/api/sectors/fund-flows`
- 做 T 监控模拟行情：`http://127.0.0.1:8000/api/stocks/t-monitor?code=600519`

做 T 监控接口返回模拟当前价、当日初始价、当前均价和相对当日初始价的涨跌幅；前端根据当日初始价计算上下价格刻度。行情为演示数据，不代表真实市场行情。

## 测试

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
```

如果先安装为本地开发包，也可以运行：

```bash
python3 -m pip install -e .
python-project
```
