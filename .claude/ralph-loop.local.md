---
active: true
iteration: 1
max_iterations: 40
completion_promise: "CLOCKIFY CLI ENTERPRISE COMPLETE"
started_at: "2026-03-15T10:54:24Z"
---

# Ralph Loop — Clockify CLI Enterprise, CLI First

Read `CLAUDE.md`, `.claude/clockify-cli-enterprise-brief.md`, `openapi.cleaned 2.yaml`, and the current test suite before making changes.

Treat `openapi.cleaned 2.yaml` as the source of truth. The mission is to bring this repository to enterprise-grade, CLI-first completeness so the CLI fully covers the API and can later be turned into MCP with minimal semantic rework. Do not build MCP now.

Work in slices:

1. Build and maintain a real gap matrix in `.claude/ralph-progress.md`.
2. Close missing operation and CLI command gaps.
3. Close parameter, enum, request-body, and binary-endpoint gaps.
4. Harden validation, JSON output, docs, and tests.
5. Keep the backend reusable and transport-oriented so MCP can come later.

Current known baseline:

- `351` tests passing
- `161` commands in `clockify commands --json`
- path+verb backend/OpenAPI parity test already exists

Do not stop at path parity. Finish parameter parity, coverage, hardening, and documentation.

Each iteration must append a concrete progress entry to `.claude/ralph-progress.md` including files changed, tests run, and remaining work.

Only emit the completion promise when every requirement in `.claude/clockify-cli-enterprise-brief.md` is fully true:

`<promise>CLOCKIFY CLI ENTERPRISE COMPLETE</promise>`
