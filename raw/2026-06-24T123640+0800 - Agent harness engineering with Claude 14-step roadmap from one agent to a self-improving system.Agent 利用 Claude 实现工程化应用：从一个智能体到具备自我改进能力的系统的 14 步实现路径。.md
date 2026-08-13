---
title: "Agent harness engineering with Claude: 14-step roadmap from one agent to a self-improving system.Agent 利用 Claude 实现工程化应用：从一个智能体到具备自我改进能力的系统的 14 步实现路径。"
source: "https://x.com/0xCodez/status/2066867539305459732"
author:
  - "[[@0xCodez]]"
published: 2026-06-16
created: 2026-06-24
description: "Everyone’s talking about loops. Almost no one is talking about what the loop runs on. 9 out of 10 builders run Claude Code on the default ha..."
tags:
  - "read"
---
![Image](https://pbs.twimg.com/media/HK76bIrX0AAnTdk?format=jpg&name=large)

Everyone’s talking about loops. Almost no one is talking about what the loop runs on. **9** out of 10 builders run Claude Code on the default harness - no rules, no subagents, no hooks, no memory.大家都在谈论循环结构。但几乎没人讨论过循环是在什么环境下运行的。十分之九的开发者都使用默认的运行环境来运行 Claude Code——没有规则约束，没有子代理，没有钩子功能，也没有内存限制。

Then they wonder why their loop produces slop. The truth is simple: **a loop is only as good as the harness underneath it**. This is the 14-step roadmap to the harness - from one agent to a system that improves itself.然后，他们就疑惑：为什么自己设计的循环结构会出问题。其实原因很简单：循环结构的优劣，完全取决于其背后的支撑机制。以下是打造这种支撑机制的 14 个步骤——从一个简单的代理程序，逐步发展成一个能够自我优化的系统。

> Follow my Substack to get fresh AI alpha: [movez.substack.com](https://movez.substack.com/)关注我的 Substack 账号，获取最新的 AI 相关内容：movez.substack.com

Loop engineering - building a system that prompts your agent on a schedule - got all the attention this month. But Addy Osmani, who wrote the long-form piece on loops, was careful to point at what sits below it:“循环工程”——也就是构建一种能够按照预定时间表来提示智能体的系统——本月受到了广泛关注。不过，撰写了关于循环工程的长篇文章的 Addy Osmani 指出，还有更重要的因素需要考虑。

“Loop engineering sits one floor above the harness. The harness is the environment one single agent runs inside. The loop is the harness, but it runs on a timer, spawns helpers, and feeds itself.”“循环工程位于‘控制框架’的上一层。‘控制框架’是单个智能体所运行的环境。而‘循环工程’其实也是‘控制框架’的一部分，只不过它是在定时器的控制下运行，会生成各种辅助组件，并能自我维持运行。”

Harness engineering is designing that environment: the model, the tools, the permissions, the context, the memory. “架构工程”就是对这种环境进行设计：包括相关的模型、工具、权限设置、使用场景以及内存管理等方面。

It’s the unglamorous layer - and it’s the one that decides whether everything above it works. A great loop on a bad harness is a fast way to produce garbage at scale.这就是那些不那么引人注目的部分——而恰恰是这些部分决定了其上方所有部件能否正常运转。如果背带上的某个环节出了问题，那么很快就会导致整个系统无法正常使用。

![Image](https://pbs.twimg.com/media/HK7ibrqWQAAUsd1?format=png&name=large)

**14 steps. 3 tiers. The foundation everything else stands on.14 级台阶。3 个层级。这是所有其他事物的基础。**

**Part 1 · what Harness is第一部分：什么是 Harness**

## 01\. A harness is the environment one agent runs inside.01. “环境”指的是某个智能体在其中运行的场所/框架。

Strip away the jargon and a harness is four things: **the model** doing the thinking, **the tools** it can reach, **the permissions** on those tools, and **the context** it reads at the start of every run.抛开那些专业术语不谈，所谓“工具包”其实包含四部分：负责进行处理的模型、该模型可以使用的工具、使用这些工具所需的权限，以及模型在每次运行时所依据的上下文信息。

That’s the whole surface. Everything else - subagents, hooks, memory - is a way of shaping one of those four.这就是整个表面而已。其他的一切——子代理、钩子、记忆等等——都不过是用来塑造这四种形态中的一种的方式罢了。

![Image](https://pbs.twimg.com/media/HK7jHWqXMAAi6sq?format=png&name=large)

The reason harness matters more than people think: the agent is a while True loop that picks a tool, runs it, looks at the result, and decides the next move. “工具链之所以比人们想象中更重要，原因在于：智能体实际上是一个循环结构——它选择某个工具来执行任务，查看执行结果后，再决定下一步该做什么。”

**The harness defines what tools exist, what the agent is allowed to do, and what it knows when it starts.** Same model, different harness, completely different agent.“框架”决定了系统中存在哪些工具、智能体可以被允许执行哪些操作，以及它在启动时具备哪些知识。同样的模型，如果使用不同的“框架”，就会产生完全不同的智能体。

## 02\. The whole harness lives in one folder. .claude/02. 所有的相关文件都保存在同一个文件夹里：.claude/

Everything that shapes your agent sits in a single directory at your project root. Learn this layout and you can read anyone’s harness at a glance:决定你的代理程序所有特性的相关文件，都保存在项目根目录下的同一个文件夹里。只要掌握了这种文件结构，你就能一目了然地了解任何人的代理程序的详细信息了。

```python
.claude/
├─ CLAUDE.md          # standing facts — read every session
├─ settings.json      # permissions, model, hooks
├─ .mcp.json          # external tool connections
├─ rules/             # path-scoped behaviors
│  ├─ tests.md
│  └─ python-types.md
├─ agents/            # subagent definitions (~30 lines each)
│  ├─ reviewer.md
│  └─ eval-runner.md
├─ skills/            # reusable workflows
│  └─ pr-checklist/
│     └─ SKILL.md
└─ agent-memory/      # what survives between runs
   └─ STATE.md
```

One rule that separates a clean harness from a mess: **keep it small enough that you can explain why every file exists.** If you can’t say what a rule, hook, or subagent is for, delete it.区分“井然有序的代码结构”与“一团糟的代码结构”的关键原则是：确保代码结构足够简洁明了，这样你才能清楚地解释每个文件的存在理由。如果无法说明某个规则、钩子或子程序的用途，那就把它删掉吧。

## 03\. Harness vs loop vs system. Three floors, don’t mix them.03. “Harness”、“loop”与“system”：这三者属于不同的概念，绝不能混为一谈。三层楼高的结构中，更不能将它们混用。

Most “my agent setup is a mess” problems come from confusing the three floors. Keep them straight:大多数“我的代理设置一团糟”的问题，都是因为把这三层结构搞混了。请务必把它们区分清楚：

- **The harness** is the runtime one agent lives in. Static configuration: model, tools, permissions, context. This issue.该“马具”指的是代理程序在运行时所处的环境。静态配置则包括模型、工具、权限以及相关上下文信息。这就是问题所在。
- **The loop** prompts the agent on a timer, spawns helpers, feeds itself. It runs on top of the harness.该循环会按照定时器来提示智能体该做什么，同时会生成各种辅助工具来协助智能体完成任务。整个系统是在“harness”框架之上运行的。
- **The self-improving system** is a loop plus memory that compounds - every run leaves the next run sharper.这种自我提升系统其实是一个循环加记忆的机制——每次运行后，系统的性能都会得到提升。

The practical version: **put standing facts in context, enforcement in hooks, procedures in skills, and isolation in subagents.**

Mixing these up - enforcement in CLAUDE.md, procedures bloating context - is the root cause of inconsistent, expensive agents.

## 04\. The default harness. What you get out of the box.

Install Claude Code, open a folder, and you already have a harness - just an empty one. The default gives you a capable model, the built-in tools (read, write, bash, search), and approval prompts on everything risky. No project context, no custom subagents, no memory.

![Image](https://pbs.twimg.com/media/HK7kUzmWMAAb5GK?format=jpg&name=large)

For a one-off task, the default is fine. For anything you do more than once, the default leaves the agent re-deriving your project from scratch every session, asking permission for safe operations, and forgetting everything when you close the terminal.

**The next ten steps are about closing that gap.**

## 05\. CLAUDE.md: standing facts, kept short.

CLAUDE.md is read at the start of every session. It’s the agent’s standing knowledge of your project - conventions, architecture, the “we don’t do it this way because of that incident.”

![Image](https://pbs.twimg.com/media/HK7tZ_EXYAA2pLb?format=png&name=large)

The single most common mistake: letting it grow into a giant procedures document that bloats every session.

The rule from practitioners running this daily: **keep the main memory file under ~500 tokens.** Standing facts go here.

Multi-step procedures go in skills (step 8). Path-specific behaviors go in rules/ files scoped to where they apply. If a section of CLAUDE.md has become a procedure rather than a fact, it belongs somewhere else.

> Read your CLAUDE.md out loud. Every line should be a fact the agent needs in every session (“we use pnpm, not npm”). If a line is a procedure (“to add a feature, first…”), move it to a skill.

If it’s a rule for one folder, move it to rules/.

## 06\. settings.json: permissions and model, set once.

The default harness asks before every risky action. That’s right when you’re watching and wrong when you’re not. settings.json is where you pre-approve the safe stuff, deny the dangerous stuff, and pick which model runs.

```python
{
  "model": "claude-sonnet-4-6",
  "permissions": {
    "autoApprove": [
      "Read(*)", "Grep(*)",
      "Bash(npm test)", "Bash(git status)"
    ],
    "deny": [
      "Bash(rm -rf*)", "Bash(git push*)",
      "Edit(.env*)", "Edit(secrets/*)"
    ]
  }
}
```

The test for what to auto-approve: **if this goes wrong, how hard is it to undo?** Cheap to undo → auto-approve.

Expensive to undo (force-push, deleting files, touching secrets) → always deny or prompt. The middle ground is fine to auto-approve if you log it.

## 07\. Subagents: isolated context for the dirty work.

A subagent is an independent Claude session launched from the main one - its own context window, its own tool list. The point isn’t parallelism for its own sake. It’s **keeping noise out of the main context.**

A research task that reads 40 files, a review pass that needs a fresh perspective, an eval run that produces a wall of logs - those belong in a subagent so they don’t pollute the main thread.

<video preload="auto" tabindex="-1" playsinline="" aria-label="Embedded video" poster="https://pbs.twimg.com/tweet_video_thumb/HK7uZLjXIAEFBge.jpg" src="https://video.twimg.com/tweet_video/HK7uZLjXIAEFBge.mp4" type="video/mp4" style="width: 100%; height: 100%; position: absolute; background-color: black; top: 0%; left: 0%; transform: rotate(0deg) scale(1.005);"></video>

![](https://pbs.twimg.com/tweet_video_thumb/HK7uZLjXIAEFBge.jpg?name=large)

GIF

The most valuable subagent in any harness is the one that **checks work the main agent did**. A model reviewing its own output is too easy on itself;

A separate reviewer with a fresh context window catches what the writer talked itself into. This is the writer-vs-checker split that makes every loop above the harness trustworthy.

## 08\. Skills: procedures the agent reuses.

A Skill is a SKILL.md file the agent runs - either when you call it with /skill-name or automatically when the task matches its description.

![Image](https://pbs.twimg.com/media/HK7u0eHWYAEFfJk?format=jpg&name=large)

Unlike a subagent, it runs in the same context window. It’s just reusable instructions that become part of the session.

The trigger to create one: **you notice yourself pasting the same instructions into every new conversation.** That’s a skill waiting to happen. A PR checklist, an eval procedure, a release process - written once, invoked forever.

And because skills are the reusable unit, they’re what makes the harness improve over time: each time the procedure fails in a new way, you add the lesson to the skill, and the next run inherits it.

## 09\. Hooks: deterministic rules the model can’t hallucinate.

Everything so far depends on the model understanding your instructions. Hooks don’t.

A hook is a shell command that fires at a fixed point in the agent lifecycle - before a tool runs, after a file changes, when the session ends- and its exit code can **block the action**. Hooks are enforcement, CLAUDE.md is suggestion.

![Image](https://pbs.twimg.com/media/HK7wfs1XQAA2nvW?format=jpg&name=large)

Two hooks earn their place in almost every harness:

- **A PreToolUse gate** that blocks dangerous commands deterministically — rm -rf, reading .env, pushing to main. Exit code 2 stops the call before it happens. The model can’t talk its way past it.
- **A PostToolUse formatter** that runs your linter or formatter after every edit. The agent never ships unformatted code because the harness formats it automatically.

```python
"hooks": {
  "PreToolUse": [{
    "matcher": "Bash",
    "command": "./.claude/hooks/block-dangerous.sh"
    // exit 2 = block the call before it runs
  }],
  "PostToolUse": [{
    "matcher": "Edit|Write",
    "command": "prettier --write \"$CLAUDE_FILE_PATH\""
  }]
}
```

Use hooks for anything that **must** happen or **must never** happen - safety, formatting, audit logging.

Don’t use them for judgment calls; that’s what the model is for. A good harness has one or two sharp hooks, not twenty.

**Part 3 · make It Compound**

## 10\. Add a loop. Now the harness runs on a timer.

A configured harness still waits for you to type. A loop makes it run on its own. The simplest version is /loop in Claude Code - a recurring prompt on a cadence.

![Image](https://pbs.twimg.com/media/HK7xHsDXsAAjaCv?format=jpg&name=large)

Pair it with /goal and the loop keeps going until an objective condition is true, checked by an independent grader rather than the agent grading itself.

```python
> /loop 30m /goal All tests pass and lint is clean.
  Triage new failures, draft fixes in claude/ branches.

▲ Claude uses the harness you built:
  - rules/ for conventions
  - reviewer subagent to check each fix
  - PreToolUse hook blocks pushes to main
✓ Looping. Independent grader decides “done.”
```

Notice what just happened: the loop didn’t add intelligence. **It re-used everything in the harness** - the rules, the reviewer subagent, the safety hook. A good harness makes a loop trivial. That’s the whole point of building the foundation first.

## 11\. Add dynamic workflows. The harness writes its own orchestration.

For tasks too complex for a single loop - massively parallel, highly structured, adversaria- Claude can write its own JavaScript harness on the fly.

That’s a dynamic workflow: agent() to spawn, parallel() to fan out, pipeline() to stream. It composes the subagents your harness defines into patterns like fan-out-and-synthesize or adversarial verification.

![Image](https://pbs.twimg.com/media/HK7x3lgWAAAokpJ?format=jpg&name=large)

The connection to harness engineering: **a dynamic workflow is only as good as the subagents and skills it can call.**

If your harness has a sharp reviewer subagent and a well-written eval skill, the workflow has good pieces to orchestrate. If the harness is empty, the workflow has nothing to work with.

The workflow is the conductor, your harness is the orchestra.

## 12\. Add memory. What the agent forgets, the harness remembers.

This is the step that turns a configured harness into a system that actually improves. The agent forgets everything between runs. **The harness doesn’t have to.**

A state file - a markdown file in agent-memory/, or a Linear board - records what was tried, what worked, what failed, what rules survived.

![Image](https://pbs.twimg.com/media/HK7yLY4XMAA9831?format=jpg&name=large)

The pattern that makes memory compound, drawn from how the strongest agents use it:

- **Write before walking away.** Every run ends by updating the state file - lessons learned, verified facts, what’s next.
- **Read at the start.** Every run begins by reading the state file and relevant skills, so it resumes instead of restarting.
- **Distill into skills.** When a lesson is general (“Windows runners need bash, not PowerShell”), it graduates from the state file into a skill, where it applies to every future project.

```python
# Project memory

## Verified facts # stop guessing about these
- prc is in dollars, not cents (checked via SELECT MIN/MAX)
- auth middleware order: rate_limit -> jwt -> rbac

## Lessons learned # distill the general ones into skills
- Windows CI runners fail TLS 1.2 in PowerShell — use bash
- Migrations on tables >1M rows must batch in 10k chunks

## Last session # resume, don’t restart
2026-06-11 · 3 fixes merged, 2 escalated. Next: verify rate-limit fix.
```

## 13\. Close the loop. Output → lesson → skill → better output.

Here’s where the three floors lock together into something that improves itself. Each run produces output. The reviewer subagent (step 7) checks it.

The result - what passed, what failed, what was learned - gets written to memory (step 12). The general lessons get distilled into skills (step 8).

**The next run inherits sharper skills and richer memory.**

That’s the whole self-improving loop, and notice it’s built entirely from harness parts:

- **Subagent** grades the work - objective check, fresh context.
- **Memory** records the verdict - survives between runs.
- **Skills** a runs it again - now with everything the last run learned.
- **The loop** runs it again - now with everything the last run learned.

The model never changed. The harness around it got sharper. That’s what “self-improving” honestly means - not a model that learns, but a harness that accumulates.

## 14\. Ship the harness. Package it. Share it. Reuse it.

A harness that works on one project is an asset.

Bundle the skills, subagents, and rules into a plugin and your whole team installs the same setup in one step - same conventions, same safety hooks, same reviewer.

![Image](https://pbs.twimg.com/media/HK70cTeWkAA7m0E?format=png&name=large)

The harness stops being your personal setup and becomes shared infrastructure.

The order to build, one last time, because order is the lesson: **get one manual run reliable on a clean harness.**

**Add the context and permissions. Add a reviewer subagent. Add memory. Then and only then wrap it in a loop.** A loop on a good harness compounds. A loop on a bad harness just bleeds faster.

## § The harness mistakes that make every loop worse

- **Running on the default.** No context, no rules, no memory - the agent re-derives your project every session.
- **A bloated CLAUDE.md.** Procedures stuffed into standing context, bloating every run. Move them to skills.
- **Enforcement in CLAUDE.md instead of hooks.** The model can ignore a suggestion. It can’t ignore a hook that exits 2.
- **One agent writing and grading its own work.** Add a reviewer subagent with a fresh context window.
- **No memory.** Every run restarts from zero. The state file is what makes tomorrow resume.
- **Wrapping a loop around a bad harness.** The loop just produces slop faster. Build the foundation first.
- **Twenty hooks.** One or two sharp ones beat a pile nobody understands.
- **Shipping a harness without scanning it.** Leaked secrets and over-broad permissions spread to everyone who installs it.

## Conclusion:

The loop gets the glory. The harness does the work.

Loop engineering is the exciting part - the agent prompting itself, running while you sleep. But a loop is just a harness on a timer.

**Everything that decides whether the output is good or garbage lives one floor down**, in the model you picked, the tools you allowed, the context you wrote, the reviewer you added, the memory you kept.

Build that floor well and everything above it compounds: the loop re-uses your subagents, the workflow orchestrates your skills, the memory makes each run sharper than the last.

**Self-improvement was never a property of the model. It’s a property of the harness you build around it.**

Pick one thing you’re not doing - probably a reviewer subagent, a safety hook, or a state file — and add it today. Keep the harness small enough to explain. Then put a loop on top, and watch the foundation do the work.