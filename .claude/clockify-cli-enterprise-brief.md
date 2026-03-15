# Clockify CLI Enterprise Brief

## Mission

Bring the Clockify CLI to enterprise-grade, CLI-first completeness against `openapi.cleaned 2.yaml`, while keeping the codebase easy to turn into an MCP server later.

The current deliverable is the CLI, not MCP. MCP-readiness is a design constraint:

- one canonical backend method per OpenAPI operation
- deterministic machine-readable JSON output
- minimal business logic in Click handlers
- consistent operation naming and parameter mapping
- clear tests and docs that can be reused for MCP tooling later

## Current Verified Baseline

As of 2026-03-15:

- `351` tests pass
- `161` CLI commands exist
- backend/OpenAPI operation parity matches at the path+verb level
- `shared-reports get` was corrected to use the reports-domain endpoint
- spec-driven operation parity test exists in `cli_anything/clockify/tests/test_openapi_parity.py`

This is not the finish line. Path parity alone is insufficient.

## Source Of Truth

- Spec: `openapi.cleaned 2.yaml`
- Repo guide: `CLAUDE.md`
- Existing parity work: `cli_anything/clockify/tests/test_openapi_parity.py`
- Existing gap tests: `cli_anything/clockify/tests/test_parity_gaps.py`, `test_cli_coverage.py`, `test_cli_gaps.py`, `test_cli_gaps_2.py`

If code and spec disagree, the spec wins unless there is a clearly documented reason not to follow it.

## Non-Negotiables

- CLI first. Do not build MCP in this loop.
- Use small focused diffs.
- Keep the mixin architecture intact unless there is a compelling reason to refactor.
- Prefer backend-first changes: backend method, then CLI command, then tests, then docs.
- Every behavior change must be covered by tests.
- No live API calls. Use mocked tests only.
- Do not weaken auth, security, retries, or error handling.
- Do not break REPL mode or `clockify commands --json`.

## Definition Of Done

Only emit the completion promise when every statement below is true:

1. Every OpenAPI operation has a matching backend method and an addressable CLI command or subcommand.
2. CLI/backend parameter mapping is spec-correct for query params, path params, request bodies, enums, and binary endpoints.
3. Any intentionally omitted field or behavior is documented with a concrete reason in repo docs.
4. Spec-driven parity tests cover more than path presence. They also guard important parameter and enum correctness where practical.
5. `clockify commands --json` remains coherent and complete for agent use.
6. Full test suite passes.
7. Docs reflect the final command surface and enterprise assumptions.
8. The backend remains a clean transport/resource layer that can later be adapted into MCP tools without re-deriving API semantics from Click handlers.

## Work Sequence

### Phase 1: Build The Real Gap Matrix

- Compare every OpenAPI operation to:
  - backend method presence
  - CLI command presence
  - parameter coverage
  - enum coverage
  - binary/file handling
  - test coverage
- Write the gap matrix into `.claude/ralph-progress.md` as a current checklist, not vague prose.

### Phase 2: Close Operation And Command Gaps

- Add any missing backend methods.
- Add any missing CLI commands.
- Preserve naming consistency with existing command groups.
- Ensure human mode and `--json` mode both work.

### Phase 3: Close Parameter And Body Gaps

- Audit request bodies for missing fields.
- Audit query parameters for missing filters, sorting, paging, and flags.
- Audit enum values against the spec, not memory.
- Audit path/domain usage, especially reports-domain endpoints and binary exports.

### Phase 4: Enterprise Hardening

- Ensure validation is strict and helpful.
- Ensure binary endpoints have a clean save-to-file UX plus JSON metadata output.
- Ensure error messages are stable and specific.
- Ensure pagination behavior matches the spec.
- Ensure config/profile behavior stays safe and deterministic.

### Phase 5: MCP-Ready Structure

Without building MCP yet:

- Keep transport logic in backend mixins.
- Avoid embedding API semantics only in Click handlers.
- Prefer reusable data-shaping helpers when repeated across commands.
- Keep command metadata and JSON outputs structured enough to map to future tools.

### Phase 6: Final Proof

- Run targeted tests during each slice.
- Run the full suite before claiming completion.
- Update `cli_anything/clockify/tests/TEST.md`.
- Update `CLAUDE.md` if the command surface or conventions changed materially.

## Iteration Output Contract

At the end of each Ralph iteration, append to `.claude/ralph-progress.md`:

- iteration number
- what gaps were closed
- files changed
- tests run and results
- remaining blockers or next slice

Do not mark work complete with a generic status line. Leave enough detail for the next iteration to continue cleanly.

## Completion Promise

Only output:

`<promise>CLOCKIFY CLI ENTERPRISE COMPLETE</promise>`

when all Definition Of Done items are unequivocally true.
