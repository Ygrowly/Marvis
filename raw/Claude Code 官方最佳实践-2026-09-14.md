> ## Documentation Index
>
> Fetch the complete documentation index at: [/docs/llms.txt](https://code.claude.com/docs/llms.txt)
>
> Use this file to discover all available pages before exploring further.

[跳转到主要内容](https://code.claude.com/docs/zh-CN/best-practices#content-area)

Claude Code 是一个代理式编码环境。与等待回答问题的聊天机器人不同，Claude Code 可以读取你的文件、运行命令、进行更改，并在你观看、重定向或完全离开的情况下自主解决问题。这改变了你的工作方式。与其自己编写代码并要求 Claude 审查，不如描述你想要什么，让 Claude 弄清楚如何构建它。Claude 会探索、规划和实现。但这种自主性仍然伴随着学习曲线。Claude 在某些约束条件下工作，你需要理解这些约束。本指南涵盖了在 Anthropic 内部团队和在各种代码库、语言和环境中使用 Claude Code 的工程师中已被证明有效的模式。有关代理循环如何在幕后工作的信息，请参阅 [Claude Code 如何工作](https://code.claude.com/docs/zh-CN/how-claude-code-works)。

* * *

大多数最佳实践都基于一个约束：Claude 的 context window 填充速度很快，随着填充，性能会下降。Claude 的 context window 保存你的整个对话，包括每条消息、Claude 读取的每个文件和每个命令输出。但这可能会很快填满。单个调试会话或代码库探索可能会生成并消耗数万个 token。这很重要，因为当 context 填充时，LLM 性能会下降。当 context window 即将满时，Claude 可能会开始”遗忘”早期的指令或犯更多错误。context window 是最重要的资源。要查看会话在实践中如何填充，请 [观看交互式演练](https://code.claude.com/docs/zh-CN/context-window)，了解启动时加载的内容以及每个文件读取的成本。使用 [自定义状态行](https://code.claude.com/docs/zh-CN/statusline) 持续跟踪 context 使用情况，并查看 [减少 token 使用](https://code.claude.com/docs/zh-CN/costs#reduce-token-usage) 了解减少 token 使用的策略。

* * *

## [​](https://code.claude.com/docs/zh-CN/best-practices\#give-claude-a-way-to-verify-its-work)  给 Claude 一种验证其工作的方式

给 Claude 一个它可以运行的检查：测试、构建、屏幕截图进行比较。这是你观看的会话和你可以离开的会话之间的区别。

当工作看起来完成时，Claude 会停止。没有它可以运行的检查，“看起来完成”是唯一可用的信号，你成为验证循环：每个错误都在等待你注意到它。给 Claude 一些能产生通过或失败的东西，循环就会自动关闭。Claude 完成工作，运行检查，读取结果，并迭代直到检查通过。检查是任何返回 Claude 可以在对话中读取的信号的东西：测试套件、构建退出代码、linter、针对固定装置比较输出的脚本，或与设计进行比较的 [浏览器屏幕截图](https://code.claude.com/docs/zh-CN/chrome)。运行 [`/verify`](https://code.claude.com/docs/zh-CN/skills#run-and-verify-your-app) 在 Claude 的检查通过后自己确认针对运行中的应用的更改。

| 策略 | 之前 | 之后 |
| --- | --- | --- |
| **提供验证标准** | _”实现一个验证电子邮件地址的函数"_ | _"编写一个 validateEmail 函数。示例测试用例： [user@example.com](mailto:user@example.com) 为真，invalid 为假， [user@.com](mailto:user@.com) 为假。实现后运行测试”_ |
| **以视觉方式验证 UI 更改** | _”让仪表板看起来更好"_ | _"\[粘贴屏幕截图\] 实现此设计。对结果进行屏幕截图并与原始设计进行比较。列出差异并修复它们”_ |
| **解决根本原因，而不是症状** | _”构建失败"_ | _"构建失败，出现此错误：\[粘贴错误\]。修复它并验证构建成功。解决根本原因，不要抑制错误”_ |

一旦检查存在，决定它对停止的限制有多严格：

- **在一个提示中**：要求 Claude 运行检查并在同一消息中迭代，如上表所示。
- **在整个会话中**：将检查设置为 [`/goal` 条件](https://code.claude.com/docs/zh-CN/goal)。单独的评估器在每次转换后重新检查它，Claude 继续工作直到目标解决。如果 Claude 停滞，Claude Code 最终会在目标仍然设置的情况下停止运行 — 请参阅 [/goal 评估如何工作](https://code.claude.com/docs/zh-CN/goal#how-evaluation-works)。
- **作为确定性门**： [Stop hook](https://code.claude.com/docs/zh-CN/hooks#stop) 作为脚本运行你的检查，并阻止转换结束直到它通过。Claude Code 覆盖 hook 并在 8 次连续阻止后结束转换。
- **通过第二意见**： [验证子代理](https://code.claude.com/docs/zh-CN/sub-agents) 或 [动态工作流](https://code.claude.com/docs/zh-CN/workflows) 检查自己的发现，有一个新鲜的模型尝试反驳结果，所以做工作的代理不是给它评分的。

每一步都用设置换取关注。提示版本适用于今天的任何任务。`/goal` 和 Stop hook 版本是让无人值守运行正确完成而无需你的东西。让 Claude 显示证据而不是声称成功：测试输出、它运行的命令及其返回的内容，或结果的屏幕截图。审查证据比自己重新运行验证要快，并且它适用于你没有观看的会话。

* * *

## [​](https://code.claude.com/docs/zh-CN/best-practices\#explore-first-then-plan-then-code)  先探索，再规划，最后编码

将研究和规划与实现分开，以避免解决错误的问题。

让 Claude 直接跳到编码可能会产生解决错误问题的代码。使用 [Plan Mode](https://code.claude.com/docs/zh-CN/permission-modes#analyze-before-you-edit-with-plan-mode) 将探索与执行分开。推荐的工作流有四个阶段：

1

探索

进入 Plan Mode，按 `Shift+Tab` 直到状态栏显示 `⏸ plan mode on`，或使用 `claude --permission-mode plan` 启动会话。Claude 读取文件并回答问题，不进行任何更改。

claude (plan mode)

```
read /src/auth and understand how we handle sessions and login.
also look at how we manage environment variables for secrets.
```

2

规划

要求 Claude 创建详细的实现计划。

claude (plan mode)

```
I want to add Google OAuth. What files need to change?
What's the session flow? Create a plan.
```

按 `Ctrl+G` 在文本编辑器中打开计划进行直接编辑，然后 Claude 继续。

3

实现

切换出 Plan Mode，通过批准计划或按 `Shift+Tab`，然后让 Claude 编码，根据其计划进行验证。

claude

```
implement the OAuth flow from your plan. write tests for the
callback handler, run the test suite and fix any failures.
```

4

提交

要求 Claude 使用描述性消息进行提交并创建 PR。

claude

```
commit with a descriptive message and open a PR
```

Plan Mode 很有用，但也增加了开销。对于范围明确且修复很小的任务（如修复拼写错误、添加日志行或重命名变量），要求 Claude 直接执行。当你对方法不确定、更改修改多个文件或你不熟悉被修改的代码时，规划最有用。如果你能用一句话描述 diff，跳过计划。

* * *

## [​](https://code.claude.com/docs/zh-CN/best-practices\#provide-specific-context-in-your-prompts)  在提示中提供具体的上下文

你的指令越精确，你需要的更正就越少。

Claude 可以推断意图，但它不能读心术。引用特定文件、提及约束，并指出示例模式。

| 策略 | 之前 | 之后 |
| --- | --- | --- |
| **限定任务范围。** 指定哪个文件、什么场景和测试偏好。 | _“为 foo.py 添加测试"_ | _"为 foo.py 编写测试，涵盖用户已注销的边界情况。避免 mock。“_ |
| **指向来源。** 指导 Claude 到可以回答问题的来源。 | _“为什么 ExecutionFactory 有这样奇怪的 api？"_ | _"查看 ExecutionFactory 的 git 历史并总结其 api 是如何形成的”_ |
| **参考现有模式。** 指向代码库中的模式。 | _“添加日历小部件"_ | _"查看主页上现有小部件的实现方式以了解模式。HotDogWidget.php 是一个很好的例子。按照模式实现一个新的日历小部件，让用户选择月份并向前/向后分页以选择年份。从头开始构建，除了代码库中已使用的库外，不使用其他库。“_ |
| **描述症状。** 提供症状、可能的位置以及”修复”的样子。 | _“修复登录错误"_ | _"用户报告会话超时后登录失败。检查 src/auth/ 中的身份验证流程，特别是 token 刷新。编写一个失败的测试来重现问题，然后修复它”_ |

当你在探索并能够改正方向时，模糊的提示可能很有用。像 `"你会改进这个文件的什么？"` 这样的提示可以表面你不会想到要问的东西。

### [​](https://code.claude.com/docs/zh-CN/best-practices\#provide-rich-content)  提供丰富的内容

使用 `@` 引用文件、粘贴屏幕截图/图像或直接管道数据。

你可以通过多种方式向 Claude 提供丰富的数据：

- **使用 `@` 引用文件**，而不是描述代码的位置。Claude 在响应前读取文件。
- **直接粘贴图像**。复制/粘贴或拖放图像到提示中。
- **提供 URL** 用于文档和 API 参考。使用 `/permissions` 来允许列表经常使用的域。
- **管道数据** 通过运行 `cat error.log | claude` 直接发送文件内容。
- **让 Claude 获取它需要的东西**。告诉 Claude 使用 Bash 命令、MCP 工具或通过读取文件来自己拉取上下文。

* * *

## [​](https://code.claude.com/docs/zh-CN/best-practices\#configure-your-environment)  配置你的环境

一些设置步骤使 Claude Code 在所有会话中显著更有效。有关扩展功能的完整概述和何时使用每个功能，请参阅 [扩展 Claude Code](https://code.claude.com/docs/zh-CN/features-overview)。

### [​](https://code.claude.com/docs/zh-CN/best-practices\#write-an-effective-claude-md)  编写有效的 CLAUDE.md

运行 `/init` 根据你的当前项目结构生成启动 CLAUDE.md 文件，然后随时间精化。

CLAUDE.md 是一个特殊文件，Claude 在每次对话开始时读取。包括 Bash 命令、代码风格和工作流规则。这给 Claude 提供了它无法从代码中推断的持久上下文。CLAUDE.md 文件没有必需的格式，但保持简短和易读。例如：

CLAUDE.md

```
# Code style
- Use ES modules (import/export) syntax, not CommonJS (require)
- Destructure imports when possible (eg. import { foo } from 'bar')

# Workflow
- Be sure to typecheck when you're done making a series of code changes
- Prefer running single tests, and not the whole test suite, for performance
```

运行 `/context` 来确认 Claude 加载了该文件。CLAUDE.md 在每个会话中加载，所以只包括广泛适用的东西。对于仅有时相关的域知识或工作流，改用 [skills](https://code.claude.com/docs/zh-CN/skills)。Claude 按需加载它们，不会使每次对话都膨胀。保持简洁。对于每一行，问自己： _“删除这个会导致 Claude 犯错吗？”_ 如果不会，删除它。膨胀的 CLAUDE.md 文件会导致 Claude 忽略你的实际指令！

| ✅ 包括 | ❌ 排除 |
| --- | --- |
| Claude 无法猜测的 Bash 命令 | Claude 可以通过读取代码弄清楚的任何东西 |
| 与默认值不同的代码风格规则 | Claude 已经知道的标准语言约定 |
| 测试指令和首选测试运行器 | 详细的 API 文档（改为链接到文档） |
| 存储库礼仪（分支命名、PR 约定） | 经常变化的信息 |
| 特定于你的项目的架构决策 | 长解释或教程 |
| 开发者环境怪癖（必需的环境变量） | 自明的实践，如”编写干净的代码” |
| 常见陷阱或非显而易见的行为 | 文件逐个描述代码库 |

如果 Claude 继续做你不想要的事情，尽管有反对的规则，该文件可能太长，规则被遗漏了。如果 Claude 问你在 CLAUDE.md 中回答的问题，措辞可能不明确。像对待代码一样对待 CLAUDE.md：当事情出错时审查它，定期修剪它，并通过观察 Claude 的行为是否实际改变来测试更改。对于检入的 CLAUDE.md，运行 [`/doctor`](https://code.claude.com/docs/zh-CN/commands#all-commands)，Claude 会建议删除它可以从代码库中推导的内容。如果 Claude 继续跳过一条指令，添加强调，如”IMPORTANT”到那一行。如果你强调许多行，没有一行会突出。将 CLAUDE.md 检入 git，以便你的团队可以贡献。该文件随时间增加价值。CLAUDE.md 文件可以使用 `@path/to/import` 语法导入其他文件。有关导入规则和 CLAUDE.md 文件可以存在的位置，请参阅 [CLAUDE.md 文件](https://code.claude.com/docs/zh-CN/memory#claude-md-files)。

### [​](https://code.claude.com/docs/zh-CN/best-practices\#configure-permissions)  配置权限

要获得更少的提示而不放弃控制，使用 `/permissions` 预先批准你信任的工具，并使用 `/sandbox` 让沙箱命令无需询问即可运行。当你想自己批准编辑和命令时，切换到手动模式。

在 Pro、Max 和 Team 计划上，auto mode 是交互式终端和 VS Code 会话的 [内置起始权限模式](https://code.claude.com/docs/zh-CN/permission-modes#eliminate-prompts-with-auto-mode)：一个单独的分类器模型审查大多数操作，而不是你，仅阻止看起来有风险的东西，如范围升级、未知基础设施或由敌对内容驱动的操作。在手动模式中，其他计划上的内置起始权限模式，Claude Code 在可能修改你的系统的操作之前询问：文件写入、Bash 命令、MCP 工具。这是安全的但繁琐。在第十次批准后，你在点击通过而不是审查。两个工具在手动模式中减少这些中断，也适用于 auto mode：

- **权限允许列表**：允许你知道是安全的特定工具，如 `npm run lint` 或 `git commit`
- **沙箱**：启用操作系统级隔离，限制文件系统和网络访问，允许 Claude 在定义的边界内更自由地工作

阅读更多关于 [权限模式](https://code.claude.com/docs/zh-CN/permission-modes)、 [权限规则](https://code.claude.com/docs/zh-CN/permissions) 和 [沙箱](https://code.claude.com/docs/zh-CN/sandboxing)。

### [​](https://code.claude.com/docs/zh-CN/best-practices\#use-cli-tools)  使用 CLI 工具

告诉 Claude Code 在与外部服务交互时使用 CLI 工具，如 `gh`、`aws`、`gcloud` 和 `sentry-cli`。

CLI 工具是与外部服务交互的最 context 高效的方式。如果你使用 GitHub，安装 `gh` CLI。Claude 知道如何使用它来创建问题、打开拉取请求和读取评论。没有 `gh`，Claude 仍然可以使用 GitHub API，但未认证的请求经常会触发速率限制。Claude 也有效地学习它不知道的 CLI 工具。尝试像 `Use 'foo-cli-tool --help' to learn about foo tool, then use it to solve A, B, C.` 这样的提示。

### [​](https://code.claude.com/docs/zh-CN/best-practices\#connect-mcp-servers)  连接 MCP 服务器

运行 `claude mcp add` 带有服务器名称和 URL 或命令来连接外部工具，如 Notion、Figma 或你的数据库。例如：`claude mcp add --transport http notion https://mcp.notion.com/mcp`。

使用 [MCP servers](https://code.claude.com/docs/zh-CN/mcp)，你可以要求 Claude 从问题跟踪器实现功能、查询数据库、分析监控数据、集成来自 Figma 的设计并自动化工作流。

### [​](https://code.claude.com/docs/zh-CN/best-practices\#set-up-hooks)  设置 hooks

使用 hooks 来处理必须每次发生且没有例外的操作。

[Hooks](https://code.claude.com/docs/zh-CN/hooks-guide) 在 Claude 工作流中的特定点自动运行脚本。与 CLAUDE.md 指令不同，hooks 是确定性的，保证操作发生。Claude 可以为你编写 hooks。尝试像 _“编写一个在每次文件编辑后运行 eslint 的 hook”_ 或 _“编写一个阻止写入迁移文件夹的 hook”_ 这样的提示。编辑 `.claude/settings.json` 直接配置 hooks，并运行 `/hooks` 来浏览配置的内容。

### [​](https://code.claude.com/docs/zh-CN/best-practices\#create-skills)  创建 skills

在 `.claude/skills/` 中创建 `SKILL.md` 文件，为 Claude 提供域知识和可重用工作流。

[Skills](https://code.claude.com/docs/zh-CN/skills) 使用特定于你的项目、团队或域的信息扩展 Claude 的知识。Claude 在相关时自动应用它们，或者你可以使用 `/skill-name` 直接调用它们。通过向 `.claude/skills/` 添加带有 `SKILL.md` 的目录来创建 skill：

.claude/skills/api-conventions/SKILL.md

```
---
name: api-conventions
description: REST API design conventions for our services
---
# API Conventions
- Use kebab-case for URL paths
- Use camelCase for JSON properties
- Always include pagination for list endpoints
- Version APIs in the URL path (/v1/, /v2/)
```

Skills 也可以定义你直接调用的可重复工作流：

.claude/skills/fix-issue/SKILL.md

```
---
name: fix-issue
description: Fix a GitHub issue
disable-model-invocation: true
---
Analyze and fix the GitHub issue: $ARGUMENTS.

1. Use `gh issue view` to get the issue details
2. Understand the problem described in the issue
3. Search the codebase for relevant files
4. Implement the necessary changes to fix the issue
5. Write and run tests to verify the fix
6. Ensure code passes linting and type checking
7. Create a descriptive commit message
8. Push and create a PR
```

运行 `/fix-issue 1234` 来调用它。对于具有你想手动触发的副作用的工作流，使用 `disable-model-invocation: true`。

### [​](https://code.claude.com/docs/zh-CN/best-practices\#create-custom-subagents)  创建自定义 subagents

在 `.claude/agents/` 中定义专门的助手，Claude 可以委托给它们来处理隔离的任务。

[Subagents](https://code.claude.com/docs/zh-CN/sub-agents) 在自己的 context 中运行，拥有自己的一组允许的工具。它们对于读取许多文件或需要专门关注而不会使你的主对话混乱的任务很有用。

.claude/agents/security-reviewer.md

```
---
name: security-reviewer
description: Reviews code for security vulnerabilities
tools: Read, Grep, Glob, Bash
model: opus
---
You are a senior security engineer. Review code for:
- Injection vulnerabilities (SQL, XSS, command injection)
- Authentication and authorization flaws
- Secrets or credentials in code
- Insecure data handling

Provide specific line references and suggested fixes.
```

明确告诉 Claude 使用 subagents： _“使用 subagent 来审查此代码的安全问题。”_

### [​](https://code.claude.com/docs/zh-CN/best-practices\#install-plugins)  安装 plugins

运行 `/plugin` 来浏览市场。Plugins 添加 skills、工具和集成，无需配置。

[Plugins](https://code.claude.com/docs/zh-CN/plugins) 将 skills、hooks、subagents 和 MCP 服务器捆绑到来自社区和 Anthropic 的单个可安装单元中。如果你使用类型化语言，安装 [代码智能 plugin](https://code.claude.com/docs/zh-CN/discover-plugins#code-intelligence) 来为 Claude 提供精确的符号导航和编辑后的自动错误检测。有关在 skills、subagents、hooks 和 MCP 之间选择的指导，请参阅 [扩展 Claude Code](https://code.claude.com/docs/zh-CN/features-overview#match-features-to-your-goal)。

* * *

## [​](https://code.claude.com/docs/zh-CN/best-practices\#communicate-effectively)  有效沟通

向 Claude 提出你会问另一位工程师的问题，对于更大的功能，让 Claude 采访你并在开始实现之前编写规范。

### [​](https://code.claude.com/docs/zh-CN/best-practices\#ask-codebase-questions)  提出代码库问题

问 Claude 你会问资深工程师的问题。

当加入新代码库时，使用 Claude Code 进行学习和探索。你可以问 Claude 你会问另一个工程师的相同类型的问题：

- 日志如何工作？
- 我如何创建新的 API 端点？
- `foo.rs` 第 134 行的 `async move { ... }` 做什么？
- `CustomerOnboardingFlowImpl` 处理哪些边界情况？
- 为什么这段代码在第 333 行调用 `foo()` 而不是 `bar()`？

以这种方式使用 Claude Code 是一个有效的入职工作流，改进了加入时间并减少了对其他工程师的负担。无需特殊提示：直接提问。

### [​](https://code.claude.com/docs/zh-CN/best-practices\#let-claude-interview-you)  让 Claude 采访你

对于更大的功能，让 Claude 先采访你。从最小的提示开始，要求 Claude 使用 `AskUserQuestion` 工具采访你。

Claude 会问你可能还没有考虑过的东西，包括技术实现、UI/UX、边界情况和权衡。将 `[brief description]` 替换为你的功能，然后再发送提示。

```
I want to build [brief description]. Interview me in detail using the AskUserQuestion tool.

Ask about technical implementation, UI/UX, edge cases, concerns, and tradeoffs. Don't ask obvious questions, dig into the hard parts I might not have considered.

Keep interviewing until we've covered everything, then write a complete spec to SPEC.md.
```

一旦规范完成，启动新会话来执行它。新会话有干净的 context，完全专注于实现，你有一个书面规范可以参考。最有用的规范是自包含的：它们命名涉及的文件和接口，说明什么在范围之外，并以端到端验证步骤结束，证明该功能有效。花在使规范精确上的时间比花在观看实现上的时间收益更大。

* * *

## [​](https://code.claude.com/docs/zh-CN/best-practices\#manage-your-session)  管理你的会话

对话是持久的且可逆的。充分利用这一点！

### [​](https://code.claude.com/docs/zh-CN/best-practices\#course-correct-early-and-often)  尽早且频繁地纠正方向

一旦发现 Claude 偏离轨道，立即纠正它。

最好的结果来自紧密的反馈循环。虽然 Claude 有时能在第一次尝试时完美解决问题，但快速纠正通常能更快地产生更好的解决方案。

- **`Esc`**：使用 `Esc` 键在 Claude 执行过程中停止它。上下文会被保留，所以你可以重新引导。
- **`Esc + Esc` 或 `/rewind`**：按两次 `Esc` 或运行 `/rewind` 来打开 rewind 菜单，恢复之前的对话和代码状态，或从选定的消息进行总结。
- **`"Undo that"`**：让 Claude 撤销其更改。
- **`/clear`**：在不相关的任务之间重置上下文。包含无关上下文的长会话可能会降低性能。

如果你在一个会话中对同一问题纠正了 Claude 两次以上，上下文就会被失败的方法所污染。运行 `/clear` 并使用更具体的提示重新开始，该提示应该包含你学到的内容。一个干净的会话配合更好的提示几乎总是比一个积累了许多纠正的长会话表现更好。

### [​](https://code.claude.com/docs/zh-CN/best-practices\#manage-context-aggressively)  积极管理上下文

在不相关的任务之间运行 `/clear` 来重置上下文。

当你接近上下文限制时，Claude Code 会自动压缩对话历史，这样可以保留重要的代码和决策，同时释放空间。在长会话期间，Claude 的上下文窗口可能会被无关的对话、文件内容和命令填满。这可能会降低性能，有时还会分散 Claude 的注意力。

- 在任务之间频繁使用 `/clear` 来完全重置上下文窗口
- 当自动压缩触发时，Claude 会总结最重要的内容，包括代码模式、文件状态和关键决策
- 为了获得更多控制，运行 `/compact <instructions>`，例如 `/compact Focus on the API changes`
- 要仅压缩对话的一部分，使用 `Esc + Esc` 或 `/rewind`，选择一个消息检查点，然后选择 **从这里总结** 或 **总结到这里**。第一个选项会压缩从该点开始的消息，同时保留较早的上下文；第二个选项会压缩较早的消息，同时保留最近的消息完整。参见 [rewind 菜单的总结选项](https://code.claude.com/docs/zh-CN/checkpointing#rewind-and-summarize)。
- 在 CLAUDE.md 中自定义压缩行为，使用诸如 `"When compacting, always preserve the full list of modified files and any test commands"` 这样的指令，以确保关键上下文在总结中得以保留
- 对于不需要保留在上下文中的问题，使用 [`/btw`](https://code.claude.com/docs/zh-CN/interactive-mode#side-questions-with-%2Fbtw)。答案永远不会进入对话历史，所以你可以检查细节而不会增加上下文。

### [​](https://code.claude.com/docs/zh-CN/best-practices\#use-subagents-for-investigation)  使用子代理进行调查

使用 `"use subagents to investigate X"` 委派研究。它们在单独的上下文中探索，保持你的主对话干净以供实现。

由于上下文是你的基本约束，使用子代理来保持研究不进入上下文。当 Claude 研究代码库时，它会读取大量文件，所有这些都会消耗你的上下文。子代理在单独的上下文窗口中运行并报告回总结：

```
Use subagents to investigate how our authentication system handles token
refresh, and whether we have any existing OAuth utilities I should reuse.
```

你也可以在 Claude 实现某些东西后使用子代理进行验证。参见 [添加对抗性审查步骤](https://code.claude.com/docs/zh-CN/best-practices#add-an-adversarial-review-step)。

### [​](https://code.claude.com/docs/zh-CN/best-practices\#rewind-with-checkpoints)  使用检查点进行 Rewind

你发送的每个开始一个轮次的提示都会创建一个检查点。你可以将对话、代码或两者都恢复到任何之前的检查点。

Claude 在每次更改前自动为文件创建快照，所以检查点可以将它们恢复。双击 `Escape` 或运行 `/rewind` 来打开 rewind 菜单。你可以仅恢复对话、仅恢复代码、同时恢复两者，或从选定的消息进行总结。参见 [Checkpointing](https://code.claude.com/docs/zh-CN/checkpointing) 了解详情。与其仔细规划每一步，你可以告诉 Claude 尝试一些冒险的事情。如果它不起作用，rewind 并尝试不同的方法。检查点与对话一起保存，所以你可以关闭终端，稍后恢复会话，并仍然可以 rewind。

检查点仅跟踪通过 Claude 的文件编辑工具所做的更改。通过 Bash 命令或外部进程所做的更改不会被捕获。这不是 git 的替代品。

### [​](https://code.claude.com/docs/zh-CN/best-practices\#resume-conversations)  恢复对话

使用 `/rename` 命名会话，并将它们视为分支：每个工作流都有自己的持久上下文。

Claude Code 在本地保存对话，所以当任务跨越多个会话时，你不必重新解释上下文。运行 [`claude --continue`](https://code.claude.com/docs/zh-CN/sessions#resume-a-session) 来从你停止的地方继续，或 `claude --resume` 来从列表中选择。给会话起描述性的名称，如 `oauth-migration`，这样你以后可以找到它们。参见 [管理会话](https://code.claude.com/docs/zh-CN/sessions) 了解完整的恢复、分支和命名控制。

* * *

## [​](https://code.claude.com/docs/zh-CN/best-practices\#automate-and-scale)  自动化和扩展

一旦你对一个 Claude 有效，通过并行会话、非交互模式和扇出模式来增加你的输出。

### [​](https://code.claude.com/docs/zh-CN/best-practices\#run-non-interactive-mode)  运行非交互模式

在 CI、pre-commit hooks 或脚本中使用 `claude -p "prompt"`。添加 `--output-format stream-json --verbose` 用于流式 JSON 输出。

使用 `claude -p "your prompt"`，你可以非交互地运行 Claude，不需要交互式提示。该运行仍然会创建一个可恢复的会话，除非你传递 `--no-session-persistence`。 [非交互模式](https://code.claude.com/docs/zh-CN/headless) 是你将 Claude 集成到 CI 管道、pre-commit hooks 或任何自动化工作流中的方式。输出格式让你以编程方式解析结果：纯文本、JSON 或流式 JSON。

```
# One-off queries
claude -p "Explain what this project does"

# Structured output for scripts
claude -p "List all API endpoints" --output-format json

# Streaming for real-time processing
claude -p "Analyze this log file" --output-format stream-json --verbose
```

第一个命令打印纯文本。`json` 格式返回一个包含 `result` 字段的单个 JSON 对象。`stream-json` 格式每行打印一个 JSON 对象，从初始化事件开始。

### [​](https://code.claude.com/docs/zh-CN/best-practices\#run-multiple-claude-sessions)  运行多个 Claude 会话

并行运行多个 Claude 会话以加快开发、运行隔离的实验或启动复杂的工作流。

选择适合你想要自己进行多少协调的并行方法，并在会话需要相互传递发现时添加消息：

- [Worktrees](https://code.claude.com/docs/zh-CN/worktrees)：在隔离的 git 检出中运行单独的 CLI 会话，以便编辑不会冲突
- [跨会话消息](https://code.claude.com/docs/zh-CN/cross-session-messaging)：让你自己运行的会话相互传递发现
- [桌面应用](https://code.claude.com/docs/zh-CN/desktop#work-in-parallel-with-sessions)：以视觉方式管理多个本地会话，每个会话都在自己的 worktree 中
- [Claude Code 在网络上](https://code.claude.com/docs/zh-CN/claude-code-on-the-web)：在云中运行会话，默认在 Anthropic 管理的基础设施上
- [Agent view](https://code.claude.com/docs/zh-CN/agent-view)：研究预览。运行 `claude agents` 来分派在后台持续运行的会话，并从一个屏幕观看它们
- [Agent teams](https://code.claude.com/docs/zh-CN/agent-teams)：实验性的，默认禁用。具有共享任务、消息和团队主管的多个会话的自动协调

除了并行化工作，多个会话启用了质量关注的工作流。新鲜的 context 改进了代码审查，因为 Claude 不会偏向于它刚刚编写的代码。例如，使用 Writer/Reviewer 模式：

| 会话 A（Writer） | 会话 B（Reviewer） |
| --- | --- |
| `为我们的 API 端点实现速率限制器` |  |
|  | `审查 @src/middleware/rateLimiter.ts 中的速率限制器实现。查找边界情况、竞态条件和与我们现有中间件模式的一致性。` |
| `这是审查反馈：[会话 B 输出]。解决这些问题。` |  |

你可以用测试做类似的事情：让一个 Claude 编写测试，然后另一个编写代码来通过它们。

### [​](https://code.claude.com/docs/zh-CN/best-practices\#fan-out-across-files)  跨文件扇出

循环遍历任务，为每个调用 `claude -p`。使用 `--allowedTools` 来限定批量操作的权限。

对于大型迁移或分析，你可以跨许多并行 Claude 调用分配工作。在 git 仓库中，运行 [`/batch <instruction>`](https://code.claude.com/docs/zh-CN/commands#all-commands) 让 Claude 将更改分割到 5 到 30 个子代理中。每个子代理在自己的 worktree 中工作并打开一个拉取请求。要从你自己的脚本驱动扇出，请循环遍历 `claude -p`：

1

生成任务列表

让 Claude 将需要迁移的文件列表写入文件，以便下一步中的循环可以读取它，使用类似 `list all 2,000 Python files that need migrating and save the list to files.txt` 的提示

2

编写脚本来循环遍历列表

```
for file in $(cat files.txt); do
  claude -p "Migrate $file from Python 2 to Python 3. Return OK or FAIL." \
    --allowedTools "Edit,Bash(git commit *)"
done
```

3

在几个文件上测试，然后大规模运行

根据前 2-3 个文件出错的情况精化你的提示，然后在完整集合上运行。`--allowedTools` 标志限制 Claude 能做什么，这在你无人值守运行时很重要。

你也可以将 Claude 集成到现有的数据/处理管道中：

```
claude -p "<your prompt>" --output-format json | your_command
```

在开发期间使用 `--verbose` 进行调试，在生产中关闭它。

### [​](https://code.claude.com/docs/zh-CN/best-practices\#run-autonomously-with-auto-mode)  使用 auto mode 自主运行

为了不间断的执行和后台安全检查，使用 [auto mode](https://code.claude.com/docs/zh-CN/permission-modes#eliminate-prompts-with-auto-mode)。分类器模型在命令运行前审查它们，阻止范围升级、未知基础设施和由敌对内容驱动的操作，同时让常规工作无提示进行。

```
claude --permission-mode auto -p "fix all lint errors"
```

当分类器在使用 `-p` 标志的非交互运行中重复阻止操作时，Claude Code 不会停止运行。请参阅 [auto mode 何时回退](https://code.claude.com/docs/zh-CN/permission-modes#when-auto-mode-falls-back) 了解发生的情况以及阈值。

### [​](https://code.claude.com/docs/zh-CN/best-practices\#add-an-adversarial-review-step)  添加对抗性审查步骤

在将任务视为完成之前，让一个子代理在新鲜的 context 中审查差异并报告缺陷。

Claude 无人值守工作的时间越长，在你将工作视为完成之前进行独立检查就越重要。在新鲜的 [subagent](https://code.claude.com/docs/zh-CN/sub-agents) context 中运行的审查者只看到差异和你给它的标准，而不是产生更改的推理，所以它按自己的条件评估结果。对于正确性检查，运行捆绑的 [`/code-review` skill](https://code.claude.com/docs/zh-CN/commands)，它在新鲜的子代理中审查当前差异以查找错误，并将发现返回到会话。要检查差异是否符合你的计划，请自己编写审查提示。命名要检查的工作、要检查的计划以及什么算作发现：

```
使用子代理根据 PLAN.md 审查速率限制器差异。检查每个要求是否已实现、列出的边界情况是否有测试，以及任务范围之外是否有任何更改。报告缺陷，而不是风格偏好。
```

因为审查者作为子代理运行，实现会话直接接收缺陷，可以修复它们并重新审查，而无需你在窗口之间复制发现。

被提示查找缺陷的审查者通常会报告一些，即使工作是健全的，因为那是它被要求做的。追逐每个发现会导致过度工程：额外的抽象层、防御性代码和针对无法发生的情况的测试。告诉审查者只标记影响正确性或陈述要求的缺陷，将其余的视为可选。

* * *

## [​](https://code.claude.com/docs/zh-CN/best-practices\#avoid-common-failure-patterns)  避免常见失败模式

这些是常见的错误。尽早识别它们可以节省时间：

- **厨房水槽会话。** 你从一个任务开始，然后问 Claude 一些不相关的东西，然后回到第一个任务。Context 充满了无关的信息。

> **修复**：在不相关的任务之间 `/clear`。

- **一次又一次地改正。** Claude 做错了什么，你改正它，它仍然是错的，你再改正。Context 被失败的方法污染。

> **修复**：在两次失败的改正后，`/clear` 并编写一个更好的初始提示，包含你学到的东西。

- **过度指定的 CLAUDE.md。** 如果你的 CLAUDE.md 太长，Claude 会忽略一半，因为重要的规则在噪音中丢失。

> **修复**：无情地修剪。如果 Claude 已经在没有指令的情况下正确地做某事，删除它或将其转换为 hook。

- **信任然后验证的差距。** Claude 产生一个看起来合理的实现，但不处理边界情况。

> **修复**：始终提供验证（测试、脚本、屏幕截图）。如果你不能验证它，不要发布它。

- **无限探索。** 你要求 Claude “调查”某些东西而不限定范围。Claude 读取数百个文件，填充 context。

> **修复**：狭隘地限定调查或使用 subagents，以便探索不会消耗你的主 context。


* * *

## [​](https://code.claude.com/docs/zh-CN/best-practices\#develop-your-intuition)  培养你的直觉

本指南中的模式不是一成不变的。它们是通常效果很好的起点，但可能不是每种情况的最优选择。有时你\_应该\_让 context 累积，因为你深入一个复杂的问题，历史很有价值。有时你应该跳过规划，让 Claude 弄清楚，因为任务是探索性的。有时模糊的提示正是你想要的，因为你想看看 Claude 如何解释问题，然后再限制它。注意什么有效。当 Claude 产生很好的输出时，注意你做了什么：提示结构、你提供的 context、你所在的模式。当 Claude 遇到困难时，问为什么。Context 太嘈杂了吗？提示太模糊了吗？任务对于一次通过来说太大了吗？随着时间的推移，你会培养没有指南能捕捉的直觉。你会知道何时具体，何时开放，何时规划，何时探索，何时清除 context，何时让它累积。

## [​](https://code.claude.com/docs/zh-CN/best-practices\#related-resources)  相关资源

- [Claude Code 如何工作](https://code.claude.com/docs/zh-CN/how-claude-code-works)：代理循环、工具和 context 管理
- [扩展 Claude Code](https://code.claude.com/docs/zh-CN/features-overview)：skills、hooks、MCP、subagents 和 plugins
- [常见工作流](https://code.claude.com/docs/zh-CN/common-workflows)：调试、测试、PR 等的分步配方
- [CLAUDE.md](https://code.claude.com/docs/zh-CN/memory)：存储项目约定和持久 context

此页面对您有帮助吗？

是否

助手

AI生成的回答可能包含错误。