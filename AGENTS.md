# 长虹证券看板 — AGENTS.md

## 📋 项目背景

本项目是一个 **A 股板块资金流与个股研判看板**，包含前后端两个子项目：

- **python-project/** — Python 后端 HTTP API 服务
  - 基于标准库 `http.server`，零外部依赖
  - 提供板块资金流模拟数据 API（`/api/sectors/fund-flows`）
  - 监听 `127.0.0.1:8000`
- **vue-project/** — Vue 3 前端看板
  - Vite 构建，单页面应用，无 Vue Router
  - 自写 CSS（无 UI 框架），Teal 主色调
  - 包含三个 Tab：主力资金、个股分析、经验教训

## 🎯 项目目标

- 提供直观的 A 股板块资金流向看板
- 支持多只个股的添加、切换和分析
- 沉淀交易经验教训，辅助复盘

## ⚠️ 约束条件

### 技术约束
- **后端**：仅使用 Python 标准库，不引入第三方依赖
- **前端**：Vue 3 + Vite，不使用 UI 框架（如 Element Plus、Ant Design 等）
- **前后端分离**：前端通过 `fetch` 调用后端 API，需配置 CORS
- **Mock 数据**：资金流数据为静态模拟数据，非真实行情

### 开发约束
- 后端启动：`cd python-project && PYTHONPATH=src python3 -m python_project`
- 前端启动：`cd vue-project && npm run dev`
- 前端默认端口 `5173`，后端默认端口 `8000`

## 💡 工作习惯

### 代码风格
- **Python**：使用 `from __future__ import annotations`，类型注解完整，使用 `dataclass`
- **Vue**：使用 Composition API（`<script setup>`），响应式数据用 `ref` / `computed`
- **CSS**：使用 CSS 变量，响应式媒体查询（760px 断点），不使用预处理器
- **命名**：变量/函数使用驼峰命名（camelCase），CSS class 使用连字符命名（kebab-case）

### 提交规范
- 提交信息使用 `type: description` 格式
- 类型：`feat`（功能）、`fix`（修复）、`style`（样式）、`refactor`（重构）、`docs`（文档）
- 示例：`feat: 个股分析新增添加个股功能`

### 协作规范
- 修改代码前先分析现有代码结构
- 前后端 API 变更需同步更新两端
- 新增功能需考虑移动端适配（760px 断点）
- 避免提交 `node_modules/`、`__pycache__/`、`.venv*/`、`dist/`、`.bak` 文件
- 优先使用 `apply_patch` 工具进行文件修改
- 复杂文本替换使用 Python 脚本处理，避免 sed 引号问题

### 页面规范
- 主力资金 Tab：展示板块资金流数据（需后端运行）
- 个股分析 Tab：个股 Tab 切换 + 分析卡片 + 添加/删除个股
- 经验教训 Tab：静态内容，展示交易经验和纪律
