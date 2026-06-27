# cap-experiment-suite

实验包生成 SKILL。输入研究问题，输出完整实验包：设计文档 + 可运行代码 + 结果（measured 或带 provenance 的 simulated）+ 发表级图 + 结构化报告。**单段一次到位**——没有"骨架 + enrich"两阶段。

## 内容

```
.claude/skills/experiment-suite/
├── SKILL.md
└── references/
    ├── 00-incremental-execution.md
    ├── 01-design-depth.md           # 设计文档：动机→假设→数据集→基线→指标→消融→预算
    ├── 02-code-quality.md           # 可运行 model.py / data.py / train.py / evaluate.py
    ├── 03-results-protocol.md       # results.json schema + measured/simulated provenance
    ├── 04-publication-figures.md    # 发表级图配方
    ├── 05-report-structure.md       # experiment_report.md 结构
    └── 06-quality-gate.md
figure_examples/                      # 3 套发表级 matplotlib 脚本（horizon sweep / heatmap / 消融）
```

## 使用

在任意 coding agent 中说：

> 帮我设计一个关于「\<问题\>」的实验

Agent 加载 `SKILL.md`，按 4 步走（理解问题/模式 → 建运行目录 → 建实验包 → 跑 quality gate）。整个过程靠 agent 自带工具完成；本 cap 不含任何 Python 运行时，也不依赖任何 LLM SDK。

## 产物路径

```
output/cap-experiment-suite/<slug>/<timestamp>/
├── experiment_design.md
├── experiment/                       # 可运行代码（model.py / data.py / train.py / evaluate.py / …）
├── results.json                      # 含 "simulated" + "provenance"
├── figures/                          # 发表级图 + 同名 make_*.py + manifest.json（仅 basename）
└── experiment_report.md
output/cap-experiment-suite/<slug>/latest -> <timestamp>
```

`cap-paper-writer` 同主题（同 slug）运行时按以下路径复用：

- `output/<slug>/latest/results.json` —— 数字与 simulated/provenance 标志来源
- `output/<slug>/latest/figures/` —— 图直接复用（manifest.json 必须存 basename）

## 优质实验要素

- 明确问题与假设：问题具体，假设可证伪，预期方向清楚。
- 数据与划分：数据来源、版本、切分、预处理和限制清楚。
- 基线完整：包含下界基线、同类基线、相邻范式基线。
- 指标完整：至少覆盖效果、代价、鲁棒性，不只报单一分数。
- 协议公平：相同数据、相同预算、相同调参口径、相同 seed 策略。
- 结果可信：报告多 seed、均值、方差，不只报最好一次。
- 归因清楚：有消融，有必要的误差分析和失败案例。
- 可复现且诚实：代码可运行，结果可追溯，simulated 与局限显式披露。

## 铁律

- 本 cap 是 skills + 图示例，**不含 Python 运行代码、禁止 LLM SDK**。
- Simulated 结果在 `results.json`、图 caption、report 顶部、下游论文 `\thanks` 中必须显式标注。
- 不允许把 simulated 当 measured 呈现；存疑就按 simulated 标注。
- `figures/manifest.json` 必须只存 basename，绝对路径会破坏下游 `\includegraphics{figures/<basename>}`。
