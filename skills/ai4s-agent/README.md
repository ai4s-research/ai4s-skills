# cap-ai4s-agent

AI4S 顶层元 SKILL。串接 4 个下游 cap 完成端到端研究包：方向 → 选题 → 综述 → 实验 → 论文。**纯 markdown**，没有 Python 运行时。

## 内容

```
.claude/skills/ai4s-agent/
└── SKILL.md       # 元剧本：slug 约定 + 4 步串接 + 披露一致性
```

## 使用

在任意 coding agent 中说：

> 给我做一份关于「\<方向 或 选题\>」的完整研究包

Agent 加载 `.claude/skills/ai4s-agent/SKILL.md` 并按约定依次加载 4 个下游 SKILL。整个过程无须本 cap 提供任何代码。

## 下游链

```
direction → cap-research-explorer  → 选题候选 → 用户拍板
topic     → cap-literature-survey  → 60+(建议 100+)引用综述
topic     → cap-experiment-suite   → 设计+代码+results.json+图
topic     → cap-paper-writer       → 8–14 页 / 200+ 引用 PDF
```

## 产物路径

每个 cap 独立写自己的 `output/<slug>/<timestamp>/`，slug 由相同主题字符串确定性算出（公式见 SKILL.md）。

## 铁律

- 本 cap 是元 SKILL，**不含任何 Python 运行代码、禁止 LLM SDK**。
- 4 个下游 cap 也都禁止 `import anthropic` / `import openai` —— 整个 cap-* 生态都是 skills + 工具，不是 autonomous program。
- 非交互运行（如 `claude --print` headless 包装）放在 cap-* 生态**之外**，cap 内永远不引入 LLM SDK。
- 每个主题在 4 个 cap 间用**同一个 slug**，公式见 SKILL.md "The slug contract" 段。
