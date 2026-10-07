# 安装与首次运行（v0.1.5）

这是一份标准 Agent Skill，同一目录可供 Claude Code 与 Codex 使用。它只通过你已经登录的 `lark-cli` 操作飞书，不依赖 Hermes。

## 前置条件

- Windows PowerShell 7 或 Windows PowerShell 5.1
- `lark-cli >= 1.0.92`
- `lark-cli whoami` 显示 `identity: user` 且 `tokenStatus: ready`
- 推荐安装飞书官方 CLI Skills，便于 Agent 获取最新命令细节：

```powershell
npx skills add larksuite/cli -y -g
```

## 安装到 Claude Code 和 Codex

在解压后的 Skill 根目录运行：

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\install.ps1 -Target Both
```

默认个人安装位置：

- Claude Code：`$env:USERPROFILE\.claude\skills\feishu-knowledge-growth`
- Codex：`$env:CODEX_HOME\skills\feishu-knowledge-growth`；未设置 `CODEX_HOME` 时为 `$env:USERPROFILE\.codex\skills\feishu-knowledge-growth`

已有同名 Skill 时脚本会停止。确认要升级才加 `-Force`：

```powershell
.\scripts\install.ps1 -Target Both -Force
```

也可以只安装到当前项目：

```powershell
.\scripts\install.ps1 -Target Both -Scope Project -ProjectPath D:\path\to\project
```

## 初始化飞书结构

先预演，不写飞书：

```powershell
.\scripts\bootstrap.ps1 `
  -SpaceId "7680151792916204527"
```

确认预演内容后再应用：

```powershell
.\scripts\bootstrap.ps1 `
  -SpaceId "7680151792916204527" `
  -Apply
```

脚本创建：

- Base：`个人知识生长系统｜工作台`
- 六张表：来源收件箱、知识节点、知识补丁、目标、成长缺口、行动与验证
- Wiki 顶层节点：首页、当前阶段、世界模型、能力模型、自我模型、实践模型、系统说明
- 当前阶段子节点：`2027秋招与当前行动主线`
- 用户配置：`$env:USERPROFILE\.knowledge-growth\config.json`

脚本不会保存 App Secret，也不会删除或覆盖已有飞书内容。若中途失败，保留已创建资源，并在配置中写入已经成功得到的 ID；再次运行前先检查飞书，避免创建重名资源。

初始化脚本只创建稳定结构，不往 Wiki 填大量占位内容。创建成功后，在 Claude Code 或 Codex 中说：

```text
使用 feishu-knowledge-growth，按 wiki-templates 初始化空白入口页；先给变更预览，我确认后再写。
```

## 第一次对话

在 Claude Code 中：

```text
/feishu-knowledge-growth 先检查系统配置，然后把这条材料作为“仅暂存”收进来源收件箱：<链接或内容>
```

在 Codex 中可直接说：

```text
使用 feishu-knowledge-growth，分析这个产品为什么火，先连接已有知识，只生成待确认补丁：<链接或内容>
```

建议第一次先用一条真实材料跑通：收件 → 分析 → 补丁预览 → 你确认 → 写入 Wiki → 创建验证行动。不要先批量导入 Obsidian。

## Windows PowerShell 5.1 乱码或 ParserError

`v0.1.1` 起，包内所有 `.ps1` 都使用 UTF-8 BOM，Windows PowerShell 5.1 和 PowerShell 7 均可正确识别中文。如果旧包出现 `浣跨敤`、`婧愮洰褰` 等乱码并伴随 `UnexpectedToken`，请改用最新版，或用以下命令把旧包脚本重新编码后再运行：

```powershell
$utf8Bom = New-Object System.Text.UTF8Encoding($true)
Get-ChildItem .\scripts\*.ps1 | ForEach-Object {
    $text = [IO.File]::ReadAllText($_.FullName, [Text.Encoding]::UTF8)
    [IO.File]::WriteAllText($_.FullName, $text, $utf8Bom)
}
```

如果旧版 `bootstrap.ps1` 在 `lark-cli.ps1` / `node.exe` 位置报 `NativeCommandError`，但手动运行 `lark-cli whoami` 正常，请升级到 `v0.1.2`。该版本会在调用 Node CLI 时暂时捕获 stdout/stderr，再根据退出码和 JSON 判断成功，不会被 PowerShell 5.1 提前终止。

## Hermes 上下文误判

如果 `lark-cli whoami` 返回：

```text
hermes context detected but lark-cli is not bound to it
```

这通常不是登录失效，而是当前 PowerShell 继承了 `HERMES_HOME`。`lark-cli 1.0.92` 会因此进入 Hermes 上下文，不再读取已经可用的普通本地 profile。本 Skill 不依赖 Hermes；不要为了解除此错误运行 `lark-cli config bind`。

先只修复当前终端：

```powershell
Get-ChildItem Env:HERMES*
Remove-Item Env:HERMES_HOME -ErrorAction SilentlyContinue
lark-cli whoami
```

确认返回的 `profile`、`onBehalfOf.userName`、`identity: user` 和 `tokenStatus: ready` 正确后，再运行 `bootstrap.ps1`。

如果每个新终端都会重新出现，先查看变量来自哪个持久范围：

```powershell
[Environment]::GetEnvironmentVariable("HERMES_HOME", "User")
[Environment]::GetEnvironmentVariable("HERMES_HOME", "Machine")
```

只有在确认不再使用 Hermes 作为全局 Agent 环境时，才删除用户级变量：

```powershell
[Environment]::SetEnvironmentVariable("HERMES_HOME", $null, "User")
Remove-Item Env:HERMES_HOME -ErrorAction SilentlyContinue
```

随后完全退出并重启 PowerShell、Claude Code 和 Codex，让新进程继承更新后的环境。该操作不会删除 Hermes 文件，也不会清除 `lark-cli` 登录；`HERMES_GIT_BASH_PATH` 不需要因为这个问题一起删除。若只有 Machine 范围有值，不要直接修改，先确认它由哪个安装程序或系统策略设置。

## Windows PowerShell 5.1 捕获中文 JSON 乱码

如果手动运行 `lark-cli whoami` 中文正常，但 `bootstrap.ps1` 中出现 `鍒樺畤骞?` 等乱码并提示“无法解析 lark-cli JSON”，说明 Node 输出的 UTF-8 被 Windows PowerShell 5.1 按旧控制台代码页解码。`v0.1.4` 会在每次 `lark-cli` 调用期间临时使用 UTF-8，并在结束后恢复原设置。

不升级时，可在当前终端临时处理：

```powershell
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[Console]::OutputEncoding = $utf8NoBom
$OutputEncoding = $utf8NoBom
```

若 `whoami` 同时显示 `tokenStatus: needs_refresh`，编码修复不能代替 OAuth。重新运行与原登录相同的 `auth login --domain ...` 或 `auth login --scope ...`，不要为了省事改成更窄的单一 scope；新登录可能替换原 token 的权限集合。

## Windows PowerShell 复杂 JSON 参数

如果 `base +base-create` 返回 `--fields invalid JSON array`，且提示使用 `--fields @file.json`，说明长 JSON 经过 `PowerShell -> lark-cli.ps1 -> Node` 时引号被重新解释。该错误发生在 CLI 本地参数校验阶段，通常尚未调用飞书 API。

`v0.1.5` 起，初始化脚本会把 `--fields` 和 `--json` 的复杂 payload 写入随机临时 UTF-8 JSON 文件，以 `@file.json` 传给 CLI，并在每次调用结束后清理。不要通过额外反斜杠或手工拼接引号规避，否则不同 PowerShell 版本下行为不一致。
