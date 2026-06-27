# cap-literature-survey

文献综述生成 SKILL。输入研究选题，输出 6–20 页、最低 60 真引用（建议 100+）、含分类法/时间线/覆盖矩阵图的完整综述（PDF + LaTeX 工程 + 分类文献表）。**单段一次到位**——没有"骨架 + enrich"两阶段。

## 内容

```
.claude/skills/literature-survey/
├── SKILL.md
└── references/
    ├── 00-incremental-execution.md
    ├── 01-bibliography-expansion.md    # WebFetch 凑 60+ 真引用（建议 100+）
    ├── 02-survey-figures.md            # 分类法/时间线/覆盖矩阵/区域图
    ├── 03-survey-section-playbook.md   # 综述 7 节结构
    ├── 04-layout-discipline.md
    └── 05-quality-gate.md
templates/survey/                        # LaTeX 起手模板
```

## 使用

在任意 coding agent 中说：

> 帮我写一篇关于「\<主题\>」的文献综述

Agent 加载 `SKILL.md`，按 4 步走（理解主题/边界 → 建运行目录 → 建综述 → 跑 quality gate）。整个过程靠 agent 自带的 WebFetch / Write / Bash 完成；本 cap 不含任何 Python 运行时，也不依赖任何 LLM SDK。

## 产物路径

```
output/cap-literature-survey/<slug>/<timestamp>/survey_paper/main.pdf
output/cap-literature-survey/<slug>/latest -> <timestamp>
output/cap-literature-survey/<slug>/<timestamp>/literature_table.md
```

`cap-paper-writer` 同主题（同 slug）运行时会按 `output/<slug>/latest/survey_paper/bibliography.bib` 复用本 cap 的 bib 作为起点。

## 铁律

- 本 cap 是 skills + LaTeX 模板，**不含 Python 运行代码、禁止 LLM SDK**。
- 每条 BibTeX 必须有 `url=`，且 URL 必须是本会话 fetch 过的。
- 300 真引用做不到（领域太小）时**如实告诉用户**，禁止造引用凑数。
