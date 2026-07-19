# Python Project

一个最小可运行的 Python 项目。

## 运行

```bash
PYTHONPATH=src python3 -m python_project
```

默认会启动 Python 后端服务：

- 健康检查：`http://127.0.0.1:8000/api/health`
- 板块资金流：`http://127.0.0.1:8000/api/sectors/fund-flows`

## 测试

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
```

如果先安装为本地开发包，也可以运行：

```bash
python3 -m pip install -e .
python-project
```
