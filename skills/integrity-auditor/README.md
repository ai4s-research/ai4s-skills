# cap-integrity-auditor

论文完整性审计 SKILL。输入一篇论文（PDF / DOI / arXiv ID / 本平台 slug），输出可复核证据格式的审计报告：分级的图像/数值/逻辑三类发现，每条发现都点明位置、变换、需要作者提供的原始材料。

不出判决，只出证据。

## 内容

```
.claude/skills/integrity-auditor/
├── SKILL.md
└── references/
    ├── 00-incremental-execution.md
    ├── 01-image-evidence.md         # 图像证据：复用 / 翻转 / 拼接 / WB 异常
    ├── 02-numerical-evidence.md     # 数值证据：n 一致性 / 均值 SD 复算 / GRIM / Benford 边界
    ├── 03-logical-evidence.md       # 逻辑证据：A→B→C 压缩 / 对照 / rescue / 复现性
    ├── 04-evidence-grading.md       # 4 级证据分级 + 可复核证据格式
    └── 05-quality-gate.md
templates/
└── audit_report.md                  # 审计报告骨架（含 cross-cap 一致性段）
```

## 使用

在任意 coding agent 中说：

> 帮我审计这篇论文：<PDF 路径 | DOI | arXiv ID | 平台 slug>

Agent 加载 `SKILL.md`，按 4 步走：

1. **识别输入** — 自动判定 PDF / DOI / slug，建运行目录。
2. **抓全套材料** — `pdftotext` 抽文本，`pdfimages` 抽 panel；slug 模式还会读 `cap-experiment-suite/.../results.json` 等平台产物。
3. **三轨并行审计**（分批、存盘、可恢复）—— 图像 / 数值 / 逻辑，每条 finding 一个文件，按 Level 1–4 分级。
4. **质量门** —— 报告必须含证据指针 + 需补 raw data；不允许写"造假"之类判决性语言。

整个过程靠 agent 自带工具完成；本 cap 不含任何 Python 运行时，也不依赖任何 LLM SDK。

## 产物路径

```
output/cap-integrity-auditor/<slug>/<timestamp>/
├── input_manifest.md            # 全部读过的材料清单
├── paper.txt                    # pdftotext 抽出的可检索文本
├── panels/                      # pdfimages 抽出的 figure panels
├── findings/
│   ├── image/<id>.md            # 一条 finding 一个文件
│   ├── numerical/<id>.md
│   └── logical/<id>.md
└── audit_report.md              # 总报告
output/cap-integrity-auditor/<slug>/latest -> <timestamp>
```

## Cross-cap 衔接（仅 slug 模式）

只读 `cap-paper-writer` 和 `cap-experiment-suite` 的同 slug 产物：

- `output/cap-paper-writer/<slug>/latest/paper/main.pdf` —— 被审论文
- `output/cap-paper-writer/<slug>/latest/paper/bibliography.bib` —— 引用核查
- `output/cap-experiment-suite/<slug>/latest/results.json` —— 数字 ground truth + provenance
- `output/cap-experiment-suite/<slug>/latest/data_contract.md` —— 数据集是否真实存在
- `output/cap-experiment-suite/<slug>/latest/figures/manifest.json` —— 论文的 figure basename 是否都在制作清单里

审计器**只读**，绝不修改其它 cap 的产物。

## 铁律

- 本 cap 是 skills + 模板，**不含 Python 运行时**。需要时（图像查重、Benford、P 值复算）调用方 agent 现场写 numpy/pillow/scipy 脚本到 run 目录里，工具脚本是 run 产物，不进 cap 仓。
- 后续如果某类工具反复需要，可放入 `forensics_tools/`（参照 `cap-experiment-suite/figure_examples/` 先例）；这与平台 anti-pattern 不冲突 —— 被禁的是"骨架 → enrich"两阶段 orchestrator 和 LLM SDK 依赖，不是确定性单一职责的工具脚本。
- **任何 finding 都必须可复核**：DOI / figure id / 截图位 / 变换说明 / 需补 raw data。
- **不出判决**：用 "inconsistent / anomalous / requires raw data / consistent with manipulation"，不用 "fraud / fabricated / intentional"。判决留给 journal 和机构。
- **找不到问题也是结果** —— 每条空轨道必须写 `_clean.md` 说明检查了什么、为什么 pass。

## 与其它 cap 的关系

- 上游：`cap-paper-writer` + `cap-experiment-suite` 产出后，可由 `cap-ai4s-agent` 触发一次自检；也可独立用于审外部论文。
- 不依赖任何其它 cap 的内部代码，只读路径约定下的产物。
