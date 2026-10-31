---
name: memory-search
description: "Search task-specific memories in a local FTS5 SQLite index."
version: 1.0.0
author: Hermes Agent (built for this device)
license: MIT
metadata:
  hermes:
    tags: [memory, search, sqlite, fts5, termux]
    related_skills: [local-memory, session-librarian]
triggers:
  - search memory for
  - find memories about
  - what do we know about
  - task-specific recall
  - local memory db
  - memsearch
---

# Memory Search (local FTS5 index)

A local SQLite database on this phone that indexes **both** Hermes conversations
(from `~/.hermes/state.db`) and persistent memory entries (from
`~/.hermes/memories/MEMORY.md` / `USER.md`) into ONE full-text store.

Use it when you need memories **related to a specific task** — e.g. "what did we
decide about VicRoads scraping?" — instead of dumping all memory or scanning raw
transcripts. No cloud, no API keys, stdlib only (sqlite3 FTS5).

DB location: `~/local-memory.db`

## When to use which tool

| Tool | Use for |
|---|---|
| `session_search` (built-in) | Conversational recall: "where did we leave off with X" — returns raw DB messages with anchors |
| `memory` tool (built-in) | Saving NEW durable facts (writes MEMORY.md/USER.md, injected every session) |
| **This skill** | Task-scoped search across conversations + memory in one ranked query; bulk recall for a topic; saving ad-hoc notes to the DB |

They complement each other: this skill's `sync` ingests what the built-in tools
produce, and its `add` stores notes that don't belong in the (bounded) MEMORY.md.

## Commands

Script: `~/.hermes/skills/note-taking/memory-search/scripts/memsearch.py`
(abbreviated below as `memsearch`)

```bash
# 1) Re-index memory entries + new conversation messages (run before search; cheap, idempotent)
python3 ~/.hermes/skills/note-taking/memory-search/scripts/memsearch.py sync

# 2) Search task-specific memories (AND semantics across tokens, bm25 ranked)
python3 .../memsearch.py search "vicroads antiforgery" --limit 10

# Filter by source: memory | user | conversation | manual | all (default all)
python3 .../memsearch.py search "scrapling playwright" --source memory

# Pin to one session
python3 .../memsearch.py search "ollama port" --session <session_id>

# Machine-readable output
python3 .../memsearch.py search "termux tls" --json

# 3) Save an ad-hoc note to the DB (does NOT touch MEMORY.md by default)
python3 .../memsearch.py add "Fold7: camera HAL quirk — use --no-awb for macro shots"
python3 .../memsearch.py add "note text" --write-file   # also append to MEMORY.md

# 4) Inspect
python3 .../memsearch.py stats          # counts per source, last sync time
python3 .../memsearch.py show <ref_key> # full text of one indexed item
python3 .../memsearch.py recent --limit 15
```

## Workflow for "recall everything about task X"

1. `sync` — pick up memory edits + messages since last index.
2. `search "<task keywords>" --limit 20` — ranked hits across all sources.
3. For any hit that looks load-bearing, `show <ref_key>` for full text.
4. Distill the answer; if a fact is durable and belongs in every session, promote
   it with the built-in `memory` tool (add to MEMORY.md/USER.md) — the DB index
   alone is NOT injected into future sessions.

## Pitfalls

- **Frozen snapshot:** MEMORY.md content injected into the system prompt is captured
  at session start. Editing MEMORY.md mid-session does not change what the model
  sees this session; it takes effect next session. The FTS index, by contrast,
  reflects disk state after `sync`.
- **Always sync before search** if the user just said something worth indexing —
  the current session's latest messages may not be in state.db yet (they are
  written as turns complete). For "what did I say earlier *this* session", read
  the conversation directly instead.
- **Query quoting:** bare words are ANDed together. Pass a quoted phrase
  (`search '"exact phrase" other'`) to force phrase matching. Tokens with special
  chars are auto-quoted by the script.
- **Dedupe keys:** memory entries dedupe on sha1(text); conversation messages on
  `msg:<state.db message id>`; manual adds on `manual:<sha1>`. Re-running sync is
  safe and prunes stale memory entries (file edits/removals), never conversation rows.
- **state.db is the source of truth for conversations** — this DB is a derived
  index. Deleting sessions from state.db does not auto-delete their rows here;
  run `sync` and they remain searchable (usually desirable).
- Android/Termux: sqlite3 FTS5 works fine (verified on this device, sqlite 3.53).
  Keep the DB in home (`~/local-memory.db`), NOT `/storage/emulated/0` (FUSE fs,
  slower + permission quirks).

## Verification

After any sync/add/search, check `stats` — counts should grow monotonically for
conversations and track MEMORY.md entry count for memory. A search that returns
0 rows for a term you know exists → re-run `sync` first, then try broader tokens
(FTS unicode61 tokenizer splits on non-alphanumerics; "anti-forgery" ≠ "antiforgery").
