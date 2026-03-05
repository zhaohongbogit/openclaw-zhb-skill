---
name: nodejs-runner
description: 执行nodejs文件完成自定义作业
version: 1.0.0
author: ZhaoHongBo
permissions: 网络访问权限（用于nodejs执行网络API调用）
---

# Node.js 脚本运行器

## 概述
安全执行 Node.js 脚本，支持文件执行、代码片段、npm 脚本和项目管理。

## 使用场景

- 运行 JS 文件："执行 script.js"
- 执行代码片段："运行这段代码 console.log('hello')"
- npm 命令："运行 npm install"
- 项目脚本："执行 npm run build"

## 实现细节

### 1. 执行现有文件
检查文件存在后执行：
```bash
node &lt;filepath&gt; [arguments]
```