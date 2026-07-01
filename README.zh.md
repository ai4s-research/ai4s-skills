<div align="center">

[![AI4S Skills — 面向科学的智能体技能](assets/banner.webp)](https://github.com/ai4s-research/ai4s-skills)

**面向 AI for Science 的开源 [Agent Skills](https://docs.claude.com/en/docs/claude-code/skills)** —— 把一个研究方向或具体选题交给任意 coding agent,产出选题探索、文献综述、可跑实验、发表级论文与完整性审计。

<p align="center"><a href="README.md">English</a> · <b>中文</b></p>

<p>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="License: MIT"></a>
  <img src="https://img.shields.io/badge/skills-7-success" alt="7 skills">
  <a href="http://makeapullrequest.com"><img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg" alt="PRs Welcome"></a>
</p>

</div>

---

## 这是什么

`ai4s-skills` 是一套持续维护的 **agent skills**,服务于 AI-for-Science 研究流程。每个 skill 都是自包含的操作手册(一个 `SKILL.md`,外加 references、LaTeX 模板和确定性工具脚本),由 coding agent —— **Claude Code、Cursor、Codex、Aider…** —— 加载并执行,直接产出最终质量的研究产物。

**设计立场 —— 是 skill,不是框架:**

- **Agent 驱动。** skill 是剧本;真正干活的是调用方 agent,用它自己的 `WebSearch` / `WebFetch` / `Edit` / `Bash`。无需安装任何编排器。
- **不绑定 LLM SDK。** skill 从不 `import anthropic` / `import openai`,跨 agent、跨模型可移植。
- **只用确定性工具。** 需要代码的地方(图像取证、发表级作图、脑图渲染)都是小而单一、依赖轻量的 Python —— 被 agent 调用,而非包裹 agent。
- **诚实为本。** 真引用(每条 BibTeX 都能追溯到 agent 本会话实际抓取过的 URL)、真图(矢量 PDF、无图表垃圾)、标注过的数字(measured / simulated / illustrative),且每份产物都永久带有"强烈建议领域专家复核"的署名。

## 有何不同

"AI 科研 agent" 这个领域正在变拥挤。`ai4s-skills` 刻意做得窄而有主张:

- **覆盖完整弧线 —— 而且含实验 _和_ 完整性审计。** 很多套件止步于"文献综述 + 写作"(有的甚至明确从不跑实验)。它覆盖 探索 → 综述 → 可跑实验 → 论文,并额外提供 **integrity-auditor**,对论文做图像复用、数值异常、逻辑缺口的取证检查 —— 真实性是一等能力,不是事后补丁。
- **真实性是设计主轴,而非一个 feature。** 每条引用都追溯到 agent 实际抓取过的 URL;每个数字都标 `measured` / `simulated` / `illustrative`(绝不把模拟当实测);每次运行都增量、持久化、可恢复,所以"完成"就是真完成,不是伪造的收尾。见 [真实性即设计](#真实性即设计)。
- **深度优先,而非广度。** 七个 skill,各自附带详尽的操作 references —— 文献扩展纪律、发表级图表 QA 合约、4 级证据分级 —— 不是对 API 的薄封装。
- **无框架、无锁定、MIT。** 纯 markdown skill + 少量确定性工具 —— 无需安装编排器、守护进程、数据库或 LLM SDK。跨 Claude Code / Cursor / Codex / Aider 可移植,且可商用。

## 7 个 skill

| Skill | 角色 | 主要产物 |
|---|---|---|
| [**ai4s-agent**](skills/ai4s-agent/SKILL.md) | 元 skill —— 端到端串起下面四个 | 下方完整研究包 |
| [**research-explorer**](skills/research-explorer/SKILL.md) | 从宽泛方向做选题探索 | `research_exploration.md` · `topic_matrix.md` · `literature_pre_survey.md` |
| [**literature-survey**](skills/literature-survey/SKILL.md) | 生成完整文献综述 | 6–20 页综述 PDF + 60+ 真引用 + LaTeX 源码 + 分类法图 |
| [**experiment-suite**](skills/experiment-suite/SKILL.md) | 实验包 | 设计文档 + 可跑代码 + `results.json`(含 provenance)+ 发表级图 + 报告 |
| [**paper-writer**](skills/paper-writer/SKILL.md) | 研究论文 | 8–14 页论文 PDF + 200+ 引用 + 4–8 图 + 表格 |
| [**mindmap-render**](skills/mindmap-render/SKILL.md) | 脑图渲染 | 把 `topic_matrix.md` 渲染成图(附 Python 脚本) |
| [**integrity-auditor**](skills/integrity-auditor/SKILL.md) | 论文完整性审计 | 图像/数值/逻辑三类发现、4 级证据分级、`audit_report.md` + 取证工具 |

### 它们如何衔接

```
方向 (direction)
   │
   ▼
[1] research-explorer ──▶ 你选定一个具体 $TOPIC
   │
   ├──▶ [2] literature-survey   (综述 PDF + bibliography.bib)
   ├──▶ [3] experiment-suite    (results.json + figures/)
   └──▶ [4] paper-writer        (复用 [2] 的 bib + [3] 的结果 → 论文 PDF)

   integrity-auditor  ──▶ 审计任意论文(外部 PDF/DOI/arXiv,或 [4] 的产物)
```

`ai4s-agent` 是元 skill,按 [1]→[4] 顺序运行。各 skill 通过确定性 **slug** + 简单的 `output/<skill>/<slug>/latest/...` 路径约定交接,无代码层耦合。

## 快速开始

### 配合 Claude Code

克隆本仓库,然后**在你想使用 skill 的项目里**运行安装脚本:

```bash
git clone https://github.com/ai4s-research/ai4s-skills

cd /path/to/your-project
/path/to/ai4s-skills/install.sh            # 全部 skill → ./.claude/skills(当前项目)
# /path/to/ai4s-skills/install.sh paper-writer                 # 或只装指定的
# SKILLS_DIR=~/.claude/skills /path/to/ai4s-skills/install.sh  # 或装到全局
```

然后在 Claude Code 里:

> 用 literature-survey 这个 skill,就 \<你的选题\> 写一篇综述。

想手动装?一个 skill 就是一个文件夹 —— 把任意 `skills/<name>/` 复制到 `~/.claude/skills/`(全局)或 `<项目>/.claude/skills/`(项目级)即可。

### 配合 Cursor / Codex / Aider / 任意 coding agent

让 agent 读对应 skill 的剧本,按步骤执行:

```
读 skills/literature-survey/SKILL.md 及其 references/,然后严格按其中规范,
就 "<你的选题>" 产出综述。
```

skill 会要求 agent 动手前先读完 `references/` —— 这些 reference 里是让产物达到发表级的纪律(文献扩展、图表规范、版式规则、质量门)。

## 仓库结构

```
ai4s-skills/
├── skills/
│   ├── ai4s-agent/          SKILL.md + references/
│   ├── research-explorer/   SKILL.md
│   ├── literature-survey/   SKILL.md + references/ + templates/survey/
│   ├── experiment-suite/    SKILL.md + references/ + figure_examples/
│   ├── paper-writer/        SKILL.md + references/ + templates/paper/
│   ├── mindmap-render/      SKILL.md + scripts/ + tests/
│   └── integrity-auditor/   SKILL.md + references/ + forensics_tools/ + templates/ + tests/
├── tools/
│   └── validate_skills.py   结构 / frontmatter 校验器(CI 中运行)
└── .github/workflows/ci.yml
```

每个 `SKILL.md` 都带 YAML frontmatter(`name`、`description`),以便 agent 发现并路由到它。

## 内置的确定性工具

这些只是 agent 调用的、单一职责的小工具,并非运行时:

- **`skills/integrity-auditor/forensics_tools/`** —— 图像重复 / ORB 匹配、面板切分、通道检查、Benford 式量级一致性、小数匹配、表格聚合一致性。
- **`skills/experiment-suite/figure_examples/`** —— 一套发表级 matplotlib 工具包(`style_kit.py`)+ 范例图脚本。
- **`skills/mindmap-render/scripts/`** —— `generate_mindmap.py`,用于渲染脑图。

## 真实性即设计

真实性贯穿每个 skill —— 它是本项目的内核,不是一个勾选项:

| 原则 | 具体含义 |
|---|---|
| **真引用** | 每条 BibTeX 都必须追溯到 agent 本会话实际抓取过的 URL —— 绝不凭记忆。 |
| **真数字** | 每个数字都标 `measured` / `simulated` / `illustrative`;模拟数据绝不冒充实测。 |
| **真实验** | `experiment-suite` 交付可跑代码 + 带 provenance 的 `results.json`。真跑一遍,实测结果就流入论文,"simulated" 声明自动去掉。 |
| **忠实记录** | 长任务增量执行、持久化进度、断点续作 —— "完成"是真完成,不是伪造的收尾。 |
| **真版式与真图** | `booktabs` 表格、`[!t]` 浮动、`~\cite{}`;矢量 PDF、内嵌字体、显式配色 —— 无图表垃圾。 |
| **诚实署名** | 每份产物永久携带"强烈建议领域专家复核"的说明。 |
| **可审计** | `integrity-auditor` 把这些纪律变成工具 —— 对任意论文(自己的或第三方的)做图像/数值/逻辑完整性检查,并给出分级证据。 |

## 贡献

欢迎新增 skill 与改进工具。一个新 skill 需要:

1. `skills/<name>/SKILL.md`,带 `name` + `description` frontmatter(`name` = 文件夹名)。
2. 可选的 `references/`、`templates/` 及确定性工具脚本。
3. 任何地方都不许 `import anthropic` / `import openai` —— skill 保持 agent 与模型无关。
4. `python tools/validate_skills.py` 通过(每个 PR 都会跑 CI)。

详见 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 许可证

[MIT](LICENSE) —— 可自由使用,包括商用。

> **免责声明。** 这些 skill 借助 AI agent 生成研究产物,输出均为草稿:**在任何引用、投稿或决策前,强烈建议由领域专家复核**。请务必核实数字、引用与论断。
