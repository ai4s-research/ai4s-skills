# cap-research-explorer

研究选题探索 SKILL。输入模糊方向，输出候选选题矩阵、创新点分析、预调研文献列表（20–30 篇）。**单段一次到位**——纯 SKILL，无 Python 运行时。

## 内容

```
.claude/skills/research-explorer/
└── SKILL.md
```

## 使用

在任意 coding agent 中说：

> 我想研究「\<方向\>」，帮我看看有哪些可行的选题

Agent 加载 `SKILL.md`，按 5 步走（理解方向 → 建运行目录 → 多维度 WebSearch+WebFetch → 出 3 份产物 → 可选下游交接）。整个过程靠 agent 自带工具完成。

## 产物路径

```
output/cap-research-explorer/<slug>/<timestamp>/
├── research_exploration.md     # 主分析报告（候选选题 + 评分 + 推荐）
├── topic_matrix.md             # 选题矩阵层级 Markdown（可被 mindmap-render 渲染）
└── literature_pre_survey.md    # 预调研文献表（20–30 条 + URL）
output/cap-research-explorer/<slug>/latest -> <timestamp>
```

用户选定具体选题后，可继续走 `cap-paper-writer` / `cap-literature-survey` / `cap-experiment-suite`，或用 `cap-mindmap-render` 把 `topic_matrix.md` 转成思维导图。

## 铁律

- 本 cap 是 SKILL，**不含 Python 运行代码、禁止 LLM SDK**。
- 候选选题只是建议、不保证原创——用户须自行验证 novelty。
- 文献条目必须有 URL 且为本会话 fetch 过的；禁止靠记忆写。
