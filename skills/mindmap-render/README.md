# cap-mindmap-render

Claude Code skill: 生成高分辨率思维导图，输出 HTML / PNG / PDF。每个大分支一个色系，子分支同色系内做明暗变化。

两种输入：

- **Markdown 大纲** → 直接渲染
- **一个主题** → 先联网调研（论文、官方文档、百科目录、行业报告等权威来源），综合成结构化大纲，再渲染

## Use

在 Claude Code 中直接提要求，例如：

> 做一个关于《XXX》的思维导图

详细工作流见 `.claude/skills/mindmap-render/SKILL.md`。

> 运行环境（Python / Playwright / Chromium）由容器预置，Skill 默认不自行安装；仅当首次运行因缺依赖失败时才会安装并重试。
