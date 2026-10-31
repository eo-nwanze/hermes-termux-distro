#!/usr/bin/env python3
"""memsearch — local FTS5 index over Hermes conversations + memory entries.

Unifies ~/.hermes/state.db (messages) and ~/.hermes/memories/*.md (memory/user
entries) into one searchable SQLite DB at ~/local-memory.db. Stdlib only.

Commands:
  sync                 re-index memory files + conversation messages (idempotent)
  search QUERY ...     ranked full-text search (--source, --session, --json, --limit)
  add TEXT [--write-file]   store a manual note (optionally also append to MEMORY.md)
  stats                index counts per source + last sync time
  show REF_KEY         print full text of one indexed item
  recent [--limit N]   most recently indexed items
"""
import argparse
import hashlib
import json
import os
import re
import sqlite3
import sys
from datetime import datetime, timezone

HERMES_HOME = os.path.expanduser(os.environ.get("HERMES_HOME", "~/.hermes"))
DB_PATH = os.path.expanduser(os.environ.get("LOCAL_MEMORY_DB", "~/local-memory.db"))
STATE_DB = os.path.join(HERMES_HOME, "state.db")
MEM_FILES = {
    "memory": os.path.join(HERMES_HOME, "memories", "MEMORY.md"),
    "user": os.path.join(HERMES_HOME, "memories", "USER.md"),
}


def sha16(s: str) -> str:
    return hashlib.sha1(s.encode("utf-8", "replace")).hexdigest()[:16]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def connect(db_path: str = DB_PATH, readonly: bool = False):
    uri = f"file:{db_path}" + ("?mode=ro" if readonly else "")
    con = sqlite3.connect(uri, uri=True)
    con.row_factory = sqlite3.Row
    return con


def init_db(con: sqlite3.Connection) -> None:
    con.executescript(
        """
        CREATE VIRTUAL TABLE IF NOT EXISTS items_fts USING fts5(
            ref_key UNINDEXED,
            source UNINDEXED,
            session_id UNINDEXED,
            title UNINDEXED,
            ts UNINDEXED,
            content
        );
        CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT);
        """
    )
    con.commit()


def parse_mem_file(path: str):
    """Split a MEMORY.md/USER.md file into entries on standalone '§' lines."""
    if not os.path.isfile(path):
        return []
    text = open(path, encoding="utf-8", errors="replace").read()
    entries = [e.strip() for e in re.split(r"(?m)^§\s*$", text)]
    return [e for e in entries if e]


def upsert(con, ref_key, source, session_id, title, ts, content):
    con.execute("DELETE FROM items_fts WHERE ref_key = ?", (ref_key,))
    con.execute(
        "INSERT INTO items_fts(ref_key, source, session_id, title, ts, content)"
        " VALUES (?,?,?,?,?,?)",
        (ref_key, source, session_id, title, ts, content),
    )


def sync(con: sqlite3.Connection, include_tools: bool = False) -> dict:
    report = {"memory": 0, "user": 0, "conversation": 0, "pruned_stale_mem": 0}

    # --- memory + user profile files -------------------------------------
    for source, path in MEM_FILES.items():
        entries = parse_mem_file(path)
        current = set()
        for i, e in enumerate(entries):
            key = f"{source}:{sha16(e)}"
            current.add(key)
            upsert(con, key, source, None, f"{source}.md entry #{i + 1}", now_iso(), e)
        # prune entries no longer present in the file (file edits/removals)
        stale = con.execute(
            "SELECT ref_key FROM items_fts WHERE source = ? AND ref_key NOT IN ({})".format(
                ",".join("?" * len(current)) if current else "NULL"
            ),
            [source] + list(current),
        ).fetchall() if current else con.execute(
            "SELECT ref_key FROM items_fts WHERE source = ?", (source,)
        ).fetchall()
        for row in stale:
            con.execute("DELETE FROM items_fts WHERE ref_key = ?", (row["ref_key"],))
        report[f"pruned_stale_{source}"] = len(stale)
        report[source] = len(entries)

    # --- conversations from state.db (read-only) ---------------------------
    if os.path.isfile(STATE_DB):
        sdb = sqlite3.connect(f"file:{STATE_DB}?mode=ro", uri=True)
        sdb.row_factory = sqlite3.Row
        roles = "('user','assistant')" if not include_tools else "('user','assistant','tool')"
        rows = sdb.execute(
            f"""
            SELECT m.id, m.session_id, m.role, m.content, m.timestamp,
                   s.source AS session_source, s.started_at
            FROM messages m LEFT JOIN sessions s ON s.id = m.session_id
            WHERE m.role IN {roles} AND m.content IS NOT NULL AND length(m.content) > 0
            """
        ).fetchall()
        for r in rows:
            ts = datetime.fromtimestamp(r["timestamp"], timezone.utc).isoformat(
                timespec="seconds"
            )
            title = f"{r['session_source'] or 'session'} {r['session_id'][:8]}"
            upsert(con, f"msg:{r['id']}", "conversation", r["session_id"], title, ts, r["content"])
        report["conversation"] = len(rows)
        sdb.close()

    con.execute(
        "INSERT OR REPLACE INTO meta(key,value) VALUES('last_sync',?)", (now_iso(),)
    )
    con.commit()
    return report


def build_fts_query(query: str) -> str:
    """Split into tokens; quote each so FTS5 treats them as exact terms/phrases.

    Tokens are ANDed (FTS5 implicit AND for space-separated terms). A token that
    already looks like a quoted phrase ("exact phrase") is kept as-is."""
    parts = []
    for tok in query.split():
        if tok.startswith('"') and tok.endswith('"') and len(tok) > 1:
            parts.append(tok.replace('"', '""'))
        else:
            parts.append('"' + tok.replace('"', '""') + '"')
    return " ".join(parts)


def fmt_ts(ts: str) -> str:
    try:
        return datetime.fromisoformat(ts).strftime("%Y-%m-%d %H:%M")
    except Exception:
        return ts


def do_search(con, query, limit, source, session_id, as_json):
    fts_q = build_fts_query(query)
    sql = """
        SELECT ref_key, source, session_id, title, ts,
               snippet(items_fts, 5, '[[', ']]', ' … ', 60) AS snip,
               bm25(items_fts) AS score
        FROM items_fts WHERE items_fts MATCH ?
    """
    args = [fts_q]
    if source and source != "all":
        sql += " AND source = ?"
        args.append(source)
    if session_id:
        sql += " AND session_id = ?"
        args.append(session_id)
    sql += " ORDER BY score LIMIT ?"
    args.append(limit)
    rows = con.execute(sql, args).fetchall()

    if as_json:
        print(
            json.dumps(
                [
                    {
                        "ref_key": r["ref_key"],
                        "source": r["source"],
                        "session_id": r["session_id"],
                        "title": r["title"],
                        "ts": r["ts"],
                        "snippet": r["snip"],
                        "score": round(r["score"], 4),
                    }
                    for r in rows
                ],
                indent=2,
            )
        )
        return

    if not rows:
        print(f"(no matches for: {query})")
        return
    for i, r in enumerate(rows, 1):
        sess = f" [{r['session_id'][:8]}]" if r["session_id"] else ""
        print(f"{i}. [{r['source']}]{sess} {fmt_ts(r['ts'])} — {r['title']}")
        print(f"   {r['snip']}")
        print(f"   ref: {r['ref_key']}")


def do_add(con, text, write_file):
    key = f"manual:{sha16(text)}"
    con.execute("DELETE FROM items_fts WHERE ref_key = ?", (key,))
    con.execute(
        "INSERT INTO items_fts(ref_key, source, session_id, title, ts, content)"
        " VALUES (?,?,?,?,?,?)",
        (key, "manual", None, "manual note", now_iso(), text),
    )
    if write_file:
        path = MEM_FILES["memory"]
        with open(path, "a", encoding="utf-8") as f:
            if os.path.getsize(path) > 0 and not open(path).read().endswith("\n"):
                f.write("\n")
            f.write("§\n" + text + "\n")
    con.commit()
    print(f"added manual note (ref: {key})" + (" [also appended to MEMORY.md]" if write_file else ""))


def do_stats(con):
    rows = con.execute(
        "SELECT source, COUNT(*) AS n FROM items_fts GROUP BY source ORDER BY n DESC"
    ).fetchall()
    last = con.execute("SELECT value FROM meta WHERE key='last_sync'").fetchone()
    total = sum(r["n"] for r in rows)
    print(f"DB: {DB_PATH} — {total} items")
    for r in rows:
        print(f"  {r['source']:<14} {r['n']}")
    print(f"last sync: {last['value'] if last else 'never'}")


def do_show(con, ref_key):
    r = con.execute(
        "SELECT ref_key, source, session_id, title, ts, content FROM items_fts WHERE ref_key=?",
        (ref_key,),
    ).fetchone()
    if not r:
        print(f"no item with ref_key {ref_key}")
        return 1
    print(f"[{r['source']}] {r['title']} @ {fmt_ts(r['ts'])}")
    if r["session_id"]:
        print(f"session: {r['session_id']}")
    print()
    print(r["content"])
    return 0


def do_recent(con, limit):
    rows = con.execute(
        "SELECT ref_key, source, title, ts FROM items_fts ORDER BY rowid DESC LIMIT ?",
        (limit,),
    ).fetchall()
    for r in rows:
        print(f"{fmt_ts(r['ts'])}  [{r['source']:<14}] {r['title']}  ({r['ref_key']})")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("sync", help="re-index memory files + conversation messages")

    s = sub.add_parser("search", help="ranked full-text search")
    s.add_argument("query", nargs="+")
    s.add_argument("--limit", type=int, default=10)
    s.add_argument("--source", default="all",
                   choices=["all", "memory", "user", "conversation", "manual"])
    s.add_argument("--session", default=None, help="restrict to one session_id")
    s.add_argument("--json", action="store_true")

    a = sub.add_parser("add", help="store a manual note in the index")
    a.add_argument("text")
    a.add_argument("--write-file", action="store_true",
                   help="also append to MEMORY.md (use sparingly — it's bounded)")

    sub.add_parser("stats", help="index counts + last sync time")
    sh = sub.add_parser("show", help="print full text of one item")
    sh.add_argument("ref_key")

    rc = sub.add_parser("recent", help="most recently indexed items")
    rc.add_argument("--limit", type=int, default=15)

    args = ap.parse_args()
    con = connect()
    init_db(con)

    if args.cmd == "sync":
        rep = sync(con)
        print(
            f"synced: memory={rep['memory']} user={rep['user']} "
            f"conversation={rep['conversation']} "
            f"(pruned stale mem/user: {rep.get('pruned_stale_memory', 0) + rep.get('pruned_stale_user', 0)})"
        )
    elif args.cmd == "search":
        do_search(con, " ".join(args.query), args.limit, args.source, args.session, args.json)
    elif args.cmd == "add":
        do_add(con, args.text, args.write_file)
    elif args.cmd == "stats":
        do_stats(con)
    elif args.cmd == "show":
        sys.exit(do_show(con, args.ref_key))
    elif args.cmd == "recent":
        do_recent(con, args.limit)


if __name__ == "__main__":
    main()
