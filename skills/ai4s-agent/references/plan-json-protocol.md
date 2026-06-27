# .vela/plan.json — planner-driven agent contract

When this repo is invoked by a **planner-driven** Vela agent
(`agents.mode = 'planner-driven'`), the agent's only step (the
"planner") must write a file at `.vela/plan.json` in the workspace.
Vela then dynamically executes the steps listed there.

## Schema

```json
{
  "title": "≤40-char human label for the overall run",
  "steps": [
    {
      "id": "kebab-case-unique-id",
      "name": "≤20 字 中文步骤名 (UI 显示)",
      "prompt": "完整 prompt; 下一个 step 直接收到这串",
      "reset": true,
      "status": "pending"
    }
  ]
}
```

### Field rules

| field | type | required | notes |
|---|---|---|---|
| `title` | string | optional | overall task label |
| `steps[].id` | string | yes | kebab-case, unique across plan |
| `steps[].name` | string | yes | ≤20 chars, Chinese OK, displayed in UI |
| `steps[].prompt` | string | yes | full prompt verbatim |
| `steps[].reset` | bool | optional, default `true` | session reset between steps |
| `steps[].status` | string | optional, default `"pending"` | one of `pending`/`running`/`done`/`failed`/`skipped` |

Vela worker invariants:
- duplicate `id` rejected → task fails fast with `PlanError`
- `status` outside the allowed set rejected
- empty / missing required fields rejected
- malformed JSON rejected

## Authoring guidelines

### Step count

Default range: **3–8 steps**. Push higher only when the user explicitly
asks for iteration (e.g. "跑 20 轮实验"). Each step is a long-running
Claude session — `PIPELINE_TIMEOUT` (currently 3600s on home-3090)
caps how much one step can chew.

### Reset semantics

Default `reset: true` for each step. Use `reset: false` only when the
next step *must* see the prior session's in-memory context. For most
research workflows the artefacts on disk are the contract; sessions
should be fresh.

### Status field

Authors should leave `status: "pending"` on every step in the freshly
written plan. The worker (or the step itself, when run) updates it.

If a step wants to declare itself complete it may overwrite its own
entry to `"done"`. The worker also applies a safety-net `"done"` after
each step in case the agent forgot (also applied if status was left as
`"running"`).

To explicitly fail-fast a step, set `"failed"`. The worker halts the
task.

### Prompt content

Each `steps[].prompt` is the full text the downstream Claude session
receives. Typical structure:

```
读 .claude/skills/<skill-name>/SKILL.md + 相关 references/。
基于 {上游产物路径}, 执行 ...
产物写到 {输出路径}.
```

Be specific about which SKILL.md to read and which `references/` to
consult. References that aren't read up-front lead to thinner output.

**`{输出路径}` 必须是具体且非 `.vela/` 的路径** —— `.vela/` 只放编排状态,
绝不放产物/中间文件(见仓库根 `AGENTS.md`「产物与中间文件路径」)。
- 走 cap 的 step → `output/cap-<name>/<slug>/<timestamp>/...`
- 不走 cap 的轻 step → 交付物 `output/<task-slug>/`,中间文件/可复用脚本 `work/...`
- 可复用的代码/脚本放 `work/`,**不要放 `/tmp/`**(跨 step 会丢、Files 里看不到)

把这个具体路径直接写进 step prompt,别让下游 step 自己猜——猜的结果就是
产物被丢进 `.vela/`。

## Validation before exit

After writing `.vela/plan.json`, the planner MUST run:

```bash
python3 -c "
import json
p = json.load(open('.vela/plan.json'))
assert isinstance(p, dict)
steps = p.get('steps')
assert isinstance(steps, list) and steps, 'steps must be non-empty list'
ids = [s['id'] for s in steps]
assert len(ids) == len(set(ids)), 'duplicate ids'
for s in steps:
    for k in ('id', 'name', 'prompt'):
        assert isinstance(s.get(k), str) and s[k].strip(), f'bad {k}'
print('OK', len(steps), 'steps')
"
```

If it raises, fix the JSON and re-run. The planner step does not exit
until this passes.

## Forbidden

- markdown code fences in `plan.json` (no ```` ```json ````)
- comments (JSON has no comments)
- initial status other than `"pending"`
- starting actual work in the planner step (writing surveys, drawing
  figures, running experiments) — the planner only produces the plan
- writing products / intermediate files anywhere under `.vela/` (it holds
  `plan.json` and step state only), or into `caps/` / `.claude/` (read-only
  skill files). Deliverables → `output/cap-*/...` or repo-root `output/<task-slug>/`;
  intermediate files & reusable scripts → `work/` (NOT `/tmp/`, which is lost
  across steps and invisible in Files)
