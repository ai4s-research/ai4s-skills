# Contributing to AI4S Skills

Thanks for your interest. This repo collects **agent skills** for AI for Science —
portable playbooks a coding agent executes to produce research artifacts.

## Adding or changing a skill

A skill lives in `skills/<name>/` and must:

1. Contain a `SKILL.md` with YAML frontmatter:
   ```yaml
   ---
   name: <name>          # must equal the folder name
   description: <when to use this skill, one sentence>
   ---
   ```
2. Keep automation in the *calling agent*. Skills describe steps; they do not ship
   an orchestrator.
3. **Never** `import anthropic`, `import openai`, or any LLM SDK. Skills stay
   agent- and model-agnostic.
4. Bundle only what the skill needs: `references/` (disciplines the agent must read),
   `templates/` (e.g. LaTeX), and small deterministic helper tools.
5. Pass validation:
   ```bash
   python tools/validate_skills.py
   ```

## Deterministic tools

Helper code (image forensics, figure kits, renderers) is welcome when it is:

- single-purpose and deterministic,
- dependency-light, and
- called *by* the agent (never wrapping or replacing it).

## Pull requests

- Keep PRs focused (one skill or one concern).
- Run the validator and any skill-local tests before opening the PR.
- CI runs `tools/validate_skills.py` and byte-compiles the Python tools.
