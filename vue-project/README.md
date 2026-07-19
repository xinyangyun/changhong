# Vue Project

一个使用 Vue 3 和 Vite 的最小前端项目。

## 安装依赖

```bash
npm install
```

## 启动开发服务器

先启动 Python 后端：

```bash
cd ../python-project
PYTHONPATH=src python3 -m python_project
```

再启动 Vue 前端：

```bash
npm run dev
```

页面会从 `http://127.0.0.1:8000/api/sectors/fund-flows` 获取板块资金流数据。
