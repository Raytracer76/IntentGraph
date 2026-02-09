# Claude Instruction Packet — IntentGraph Multi-Language Sprint (for Grindbot)

You are working in the **IntentGraph** repo. The goal is to make IntentGraph a reliable “repo brain” for **Grindbot** by adding support for the languages Grindbot actually uses (TypeScript/JavaScript first), while keeping everything **deterministic, test-driven, and parallelizable**.

## 0) Operating Rules (non-negotiable)

### Branching + Parallelization
- Work is split **one branch per language**, **one agent per language**.
- No agent edits files outside their “lane” (see §3).
- Every branch becomes a PR; **merge only on green**.
- Commit discipline: **commit only when tests are green** (local + CI).

### Determinism
- Same repo + same inputs → **identical outputs** (ordering, IDs, JSON, fingerprint).
- No timestamps, no randoms, no environment-dependent content.

### Testing
- Each branch must add:
  - Fixtures (`fixtures/<lang>/...`)
  - Tests validating symbol extraction + import edges + deterministic IR ordering
- Don’t weaken existing tests. Don’t delete golden snapshots unless necessary and justified.

---

## 1) Objective (what to build)

Extend IntentGraph so the orchestrator can:
1) **Index** a repo (symbols + relationships) in TS/JS-heavy codebases (Grindbot).
2) **Query** reliably using the AI-native interface.
3) **Fingerprint** a repo reproducibly (stable hash) based on canonicalized analysis output.

Prioritize:
- TypeScript ✅ (highest value)
- JavaScript ✅ (should largely reuse TS machinery)
- JSON ✅ (package.json, tsconfig, config files)
- Everything else later.

---

## 2) Repo Structure & Shared Contract

We use a single language parser interface (“Language Parser Contract”). Each language implementation MUST output a normalized IR.

### Language Parser Contract (must implement)
Input:
- `path: str`
- `text: str`

Output IR (minimum fields):
- file metadata:
  - `path`, `language`, `size_bytes` (or derivable), `sha256` of file text
- symbols:
  - `symbol_id` (stable), `name`, `kind`, `span` (start/end line/col), `exported/public` flags when meaningful
- references (when feasible):
  - imports/require edges at minimum
- dependency edges:
  - list of `from_path -> to_path` edges for imports

### Deterministic IDs
Symbol IDs MUST be stable and derived from:
- canonical file path (posix normalized)
- kind
- name
- span
Then hash (sha256) and use a readable prefix if desired.

### Ordering Rules
Always sort:
- files by path
- symbols by (path, span.start, kind, name)
- edges by (from_path, to_path, import_name if present)

---

## 3) Parallel Work Plan: branches, lanes, acceptance

### Branches to create (coordinator does this immediately)
- `feat/lang-ts`
- `feat/lang-js`
- `feat/lang-json`
(Optional later: `feat/lang-md`, `feat/lang-yaml`)

### Lane boundaries (agents MUST respect)
Each language branch may edit ONLY:
- `intentgraph/parsers/<lang>/...` (or equivalent parser dir)
- `fixtures/<lang>/...`
- `tests/test_<lang>_*.py` (or equivalent)
- Minimal registry wiring:
  - a single central registry file if required (touch lightly; avoid conflicts)

Everything else is off-limits unless explicitly necessary for the contract.

---

## 4) Assignment: one agent per language (run in parallel)

### Agent A: TypeScript (branch: feat/lang-ts)
Deliverables:
- TS parser implementation
- Extract:
  - imports/exports
  - functions, classes, interfaces, types, enums (at minimum)
  - file→file import edges
- Fixtures:
  - TS sample project snippets with representative patterns
- Tests:
  - symbol count sanity checks
  - expected import edges
  - deterministic ordering snapshot or canonical JSON comparison

### Agent B: JavaScript (branch: feat/lang-js)
Deliverables:
- JS parser implementation (can reuse TS machinery if same parser)
- Extract:
  - require/import edges
  - function/class declarations at minimum
- Fixtures + tests analogous to TS but JS flavored.

### Agent C: JSON (branch: feat/lang-json)
Deliverables:
- JSON parser implementation
- Extract:
  - top-level keys as “symbols” (optional but useful)
  - dependency edges for `package.json`:
    - dependencies/devDependencies/peerDependencies -> package names
    - treat as special “external dependency edges”
- Fixtures: package.json, tsconfig, typical config patterns
- Tests verifying:
  - dependencies extracted deterministically
  - stable ordering
  - stable fingerprint impact when deps change

---

## 5) Coordinator responsibilities (Claude main instance)

You are the coordinator. You must:
1) Create the branches listed above from up-to-date main.
2) Spawn/assign worker agents to each branch.
3) Keep the parser contract stable during the sprint.
4) Pull each branch, run full test suite, open PRs.
5) Resolve conflicts (prefer rebasing worker branches onto updated main).
6) Merge PRs only when CI green.

---

## 6) Fingerprinting requirement (shared, but implement carefully)

Fingerprint should be stable across machines.

Canonical fingerprint input should include:
- sorted list of file records: (path, sha256(file text))
- sorted list of symbol records: (symbol_id, kind, name, span, exported)
- sorted list of dependency edges: (from_path, to_path or external_name, edge_kind)

Compute:
- canonical JSON serialization with sorted keys
- sha256 of that canonical JSON = `repo_fingerprint_sha256`

If fingerprint logic already exists for Python, extend it so multi-language outputs are included.

IMPORTANT:
- Agents should not fight over fingerprint code. Prefer coordinator integrates final fingerprint wiring after merges if needed.

---

## 7) Acceptance Criteria (what “done” means)

For each language PR:
- ✅ Parser implemented behind the common contract
- ✅ Fixtures added
- ✅ Tests added and passing
- ✅ Deterministic output verified (stable snapshots or canonical comparisons)
- ✅ Does not break Python analysis

After all merges:
- ✅ Running IntentGraph on Grindbot repo yields:
  - TS/JS symbol extraction
  - import edges
  - stable repo fingerprint across repeated runs
- ✅ AI-native interface can query TS/JS codebases without rescanning chaos

---

## 8) PR Checklist (must be included in each PR description)

- [ ] Branch scope limited to assigned lane
- [ ] Added fixtures for language
- [ ] Added tests for language
- [ ] Verified determinism (repeat run equals same output)
- [ ] Full test suite green locally
- [ ] CI green
- [ ] No unrelated refactors

---

## 9) Commands (expected workflow)

Coordinator:
- create branches
- assign agents
- run full suite per PR

Worker agent:
- checkout branch
- implement parser + fixtures + tests
- run tests
- commit on green
- push branch
- open PR

---

## 10) Notes on parser tech choice

If tree-sitter is blocked in some environments, **do not hard-fail imports**:
- Use lazy initialization (as done for Python)
- Provide graceful fallback behavior
- Tests should avoid relying on unavailable system components

---

## Final instruction
Execute this plan with maximal parallelism. No chatter. No scope creep. Merge only on green.
