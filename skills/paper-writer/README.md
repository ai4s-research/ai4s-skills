# cap-paper-writer

研究论文生成 SKILL。输入主题（可选 measured experiment data），输出 200+ 引用、4–8 张发表级图、7 节正文的完整论文（PDF + LaTeX 工程）。**单段一次到位**——没有"骨架 + enrich"两阶段。

## 内容

```
.claude/skills/paper-writer/
├── SKILL.md
└── references/
    ├── 00-incremental-execution.md     # 分批 / 持久化 / 续跑
    ├── 01-bibliography-expansion.md    # 用 WebFetch + WebSearch 凑 200+ 真引用
    ├── 02-figures-publication-grade.md # TikZ / matplotlib / seaborn 配方
    ├── 03-section-playbook.md          # 各节结构、长度、引用密度
    ├── 04-layout-discipline.md         # booktabs / [!t] floats / 作者+免责 footnote
    ├── 05-quality-gate.md              # G1–G8 硬门、S1–S5 软门
    └── 06-experiment-provenance.md     # measured / simulated / illustrative 三档
templates/paper/                         # LaTeX 起手模板（main.tex + sections/ + figures/）
```

## 使用

在任意 coding agent 中（Claude Code、Cursor、Aider、Codex…）说：

> 帮我写一篇关于「\<主题\>」的研究论文

Agent 加载 `SKILL.md`，按其中 4 步走（理解需求 → 建运行目录 → 建论文 → 跑 quality gate）。整个过程靠 agent 自带的 WebFetch / Write / Bash 工具完成；本 cap 不含任何 Python 运行时，也不依赖任何 LLM SDK。

## 产物路径

```
output/cap-paper-writer/<slug>/<timestamp>/paper/main.pdf
output/cap-paper-writer/<slug>/latest -> <timestamp>
```

## 跨 cap 联动（路径约定）

如果 `cap-literature-survey` 或 `cap-experiment-suite` 已为同一主题（同一 slug）跑过，本 SKILL 会按约定路径复用：

- `output/cap-literature-survey/<slug>/latest/survey_paper/bibliography.bib` → 作为 bib 起点（仍需补到 200+）
- `output/cap-experiment-suite/<slug>/latest/results.json` → 数字与 provenance flag 来源
- `output/cap-experiment-suite/<slug>/latest/figures/` → 图复用

## 铁律

- 本 cap 是 skills + LaTeX 模板，**不含任何 Python 运行代码、也禁止 `import anthropic` / `import openai`**。
- 每条 BibTeX 必须有 `url=`，且 URL 必须是 agent 本次会话内 fetch 过的；不允许靠记忆写引用。
- Simulated 数字必须在 title `\thanks` + abstract + 每张图/表 caption 中保留可见标记。
- 200+ 真引用做不到（主题太小）时**如实告诉用户**，不允许造引用凑数。
