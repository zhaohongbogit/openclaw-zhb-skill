---
name: android-builder-capp
description: 皇包车应用CAPP打包
version: 1.0.0
author: ZhaoHongBo
permissions: 网络访问权限（用于拉取源码）
---

# android-builder-capp

## Description

从 Git 仓库拉取 Android 工程代码，并修改文件目录README.md部分，重新提交仓库。

## Triggers

当用户有类似需求时使用本 Skill：

- “打一个皇包车旅行/CAPP测试/生产包”
- “从 git 拉一下 Android 代码然后打个包”
- “编译皇包车 Android APP，出一个 release 包”
- “打一个最新的 debug APK 发给我”
- “帮我更新到最新代码并重新打包”

## Requirements

- 本机已安装：
    - Git

## How To Use

### 1. 从零开始克隆并打包

1. 根据 `config.json` 中的 `repoUrl` 和 `localPath`：
    - 如果 `localPath` 目录不存在：执行 `git clone`
    - 如果已经存在：执行 `git pull` 更新到最新 `branch`
2. 切换到工程目录：
    - `cd <localPath>`
3. 确保 `gradlew` 有可执行权限：
    - `chmod +x ./gradlew`
4. 执行构建任务（例如 release 包）：
    - `./gradlew :<module>:assembleRelease`
5. 构建成功后，从：
    - `app/build/outputs/apk/release/`（或对应 module 目录）
      找到最新生成的 APK 文件。
6. 返回信息给用户，包含：
    - 构建结果：成功 / 失败
    - APK 路径
    - 可选：文件大小、版本号

### 2. 修改构建类型（debug/release）

- 如用户说：“打一个 debug 包”：
    - 将 `gradleTask` 临时改为：`assembleDebug`
    - 或通过参数传入（如果你用 nodejs-runner/脚本支持参数）

## Example Flows

### Example 1：打一个 release 包

**User:**  
“帮我从 git 拉取皇包车 Android 代码并打一个 release 包。”

**Agent (Internal Steps):**

读取 config.json

1. 运行：
```shell
if [ ! -d "/root/android/huangbaoche-app" ]; then
git clone git@github.com:xxx/huangbaoche-app.git /root/android/huangbaoche-app
fi

cd /root/android/huangbaoche-app
git fetch origin
git checkout main
git pull

chmod +x ./gradlew
./gradlew :app:assembleRelease
```

2. 查找生成的 APK，比如：

/root/android/huangbaoche-app/app/build/outputs/apk/release/app-release.apk

回复用户构建结果和 APK 路径。

### Example 2：打一个 debug 包

**User:**  
“打个最新的 debug APK 给我测试。”

**Agent:**

在同样目录下执行：

```shell
./gradlew :app:assembleDebug
```