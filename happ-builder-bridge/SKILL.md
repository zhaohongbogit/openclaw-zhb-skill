---
name: happ-builder-bridge
description: 执行皇包车APP源码拉取改动提交过程
version: 1.0.0
author: ZhaoHongBo
permissions: 网络访问权限（用于拉取源码），执行shell命令权限
allowed-tools: Bash(npm:*) Bash(npx:*) Bash(openclaw:*) Bash(curl:*) Read Write WebFetch
---

# APP打包

## 概述
将 OpenClaw 的自然语言指令，转换为对私有 GitLab 仓库的自动提交，从而触发已有的 GitLab Runner 流水线。

## 场景说明

- 私有 GitLab 仓库：`https://gitlab.hbc.tech/kmp/kmp-hbc-app.git`
- CI 已经使用 GitLab Runner + happ-builder 正常构建打包移动应用
- 构建触发逻辑：当 `hongbo/test` 分支有新的提交时，流水线自动执行打包
- 这个技能只负责：
    - 拉取/更新代码
    - 修改 `README.md`，追加一行“自动打包日期”
    - 提交到 `hongbo/test` 分支并推送

> 也就是说：**本技能只做“自动改 README + 提交 + push”这一步，后续构建/打包动作全部交给现有 GitLab CI/happ-builder 处理。**



## 触发方式（自然语言）

当用户说出以下类似指令时，应触发本技能逻辑：

- “帮我打 CAPP 包”
- “帮我打皇包车旅行的包”
- “帮我用 happ-builder 触发一次打包”
- 以及同义句（可以包含“CAPP”“皇包车”“旅行”“打包”“构建”等关键词）

Agent 需要：

1. 识别到这是 “**触发 happ-builder 打包**” 的意图；
2. 将本次触发的“打包类型”作为一个标签，用于写入 README 和提交信息：
    - “CAPP 包” → `trigger_type = "CAPP"`
    - “皇包车旅行的包” → `trigger_type = "HBC_TRAVEL"`
    - 如果无法区分，使用默认：`trigger_type = "DEFAULT"`

---

## 环境要求

宿主机（运行 OpenClaw 的机器）需要具备：

1. Git 环境：
    - 安装了 `git`
    - 已配置好访问 `https://gitlab.hbc.tech` 的凭证（SSH key 或 HTTPS token）
    - 能正常 clone/pull/push 仓库 `https://gitlab.hbc.tech/kmp/kmp-hbc-app.git`

2. 文件系统权限：
    - Agent 必须具备 `exec` 和 `read/write` 能力，能：
        - 在本地执行 `git` 命令和 `date` 命令
        - 读写项目目录下的 `README.md`

3. 本地代码目录（建议路径，可按需修改）：
    - `/data/projects/kmp-hbc-app`
    - 若目录不存在，应由本技能自动 `git clone` 创建

> 如需调整路径，请在下文“实现步骤”中的 `REPO_DIR` 和 `GIT_URL` 一并修改。

---

## 实现步骤（给 Agent 的执行指令）

> 下面是**伪代码级别**的步骤，Agent 在具备 `exec/FS` 能力的会话中应按此顺序执行。

### 1. 准备变量

根据用户指令识别出：

- `trigger_type`：
    - 包含“CAPP”、“capp” → `CAPP`
    - 包含“皇包车旅行”、“旅行” → `HBC_TRAVEL`
    - 否则 → `DEFAULT`

固定参数：

- `GIT_URL = "https://gitlab.hbc.tech/kmp/kmp-hbc-app.git"`
- `REPO_DIR = "/data/projects/kmp-hbc-app"`
- `TARGET_BRANCH = "hongbo/test"`

获取当前时间（用于 README 和 commit message），例如：

```bash
TIMESTAMP=$(date "+%F %T")  # 形如 2026-03-06 10:40:00  
```

### 2. 确保本地仓库存在

```bash
if [ ! -d "$REPO_DIR/.git" ]; then
  git clone "$GIT_URL" "$REPO_DIR"
fi
```

### 3. 切换到目标分支并更新

```bash
cd "$REPO_DIR"

git fetch origin

# 如果本地不存在 TARGET_BRANCH，则从远端创建跟踪分支
if ! git rev-parse --verify "$TARGET_BRANCH" >/dev/null 2>&1; then
  git checkout -b "$TARGET_BRANCH" "origin/$TARGET_BRANCH" || git checkout -b "$TARGET_BRANCH" origin/main
else
  git checkout "$TARGET_BRANCH"
fi

git pull origin "$TARGET_BRANCH" || true
```
> 注：如果远端没有 hongbo/test 分支，而是从 main 或其他默认分支创建，需根据实际情况调整上面 origin/main 的名字。

### 4. 修改 README.md，追加自动打包记录

要求：在 README.md 末尾追加一行记录，例如：

```
Auto build trigger at 2026-03-06 10:40:00 [CAPP]
```

伪代码：

```bash
README_FILE="$REPO_DIR/README.md"

if [ ! -f "$README_FILE" ]; then
  # 若不存在，则创建一个简单的 README
  echo "# kmp-hbc-app" > "$README_FILE"
  echo "" >> "$README_FILE"
fi

echo "Auto build trigger at ${TIMESTAMP} [${trigger_type}]" >> "$README_FILE"
```

### 5. 提交并推送到 hongbo/test 分支

```bash
cd "$REPO_DIR"
git add README.md

# 如果没有变更则不提交
if ! git diff --cached --quiet; then
  git commit -m "chore: auto build trigger (${trigger_type}) at ${TIMESTAMP}"
  git push origin "$TARGET_BRANCH"
else
  # 已经有相同内容，不重复提交，可直接视为成功
  echo "No changes to commit."
fi
```

### 6. 返回给用户的信息

执行完成后，Agent 向用户返回简要结果，例如：

* 成功示例：
> 已触发 happ-builder 构建。
*仓库：https://gitlab.hbc.tech/kmp/kmp-hbc-app.git
*分支：hongbo/test
*触发类型：CAPP
*时间：2026-03-06 10:40:00
*请在 GitLab 上查看对应流水线状态。

* 若 push 失败（权限 / 网络等问题），应返回错误信息摘要和建议（例如检查 Git 凭证）。

---

## 安全与注意事项

* 确保运行 OpenClaw 的系统用户使用的 Git 凭证只具备必要的仓库访问权限，避免误操作其他项目。
* 技能只修改 README.md，不应碰其他文件，避免引入非预期变化。
* 如需支持更多“打包类型”，只需扩展 trigger_type 的映射规则和 README 追加的标记内容。

---

## 之后怎么用这个技能

当你在一个**有 exec/FS 权限的 OpenClaw 会话**里，对我说：

- “帮我打 CAPP 包”
- “帮我打皇包车旅行的包”

我就会按 `SKILL.md` 里这套流程：

1. 拉/更新 `kmp-hbc-app` 仓库；
2. 切 `hongbo/test` 分支；
3. 在 `README.md` 末尾加一行带时间的记录；
4. 提交并推送；
5. 然后由 GitLab Runner + happ-builder 去做后面的打包。

---