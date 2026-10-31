---
name: github-fetch
description: "Fetch GitHub files or clone repos without credentials."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [GitHub, Retrieval, Credentials, Tarball, REST-API]
    related_skills: [github-repo-management]
---

# GitHub Content Fetch

## Purpose

Use this skill when you need to read a file from, or clone, a GitHub repo but have no GitHub credentials (no `gh` login, no `GITHUB_TOKEN`) — i.e. in a credential-less or proot/container environment where `git clone` and authenticated REST endpoints refuse anonymous access.

## When to Use

- `git clone` on GitHub fails with `could not read Username` or a credential prompt.
- Authenticated REST endpoints return `401` (no token available).
- You need to read a single file, list a repo's tree, or clone a **public** repo without signing in.

This is a *fallback* path. If `gh`/git + token works, use `github-repo-management` instead.

## Always-on rules

- When git clone or an authenticated REST call fails with `could not read Username` (git) or `401` (REST), GitHub is refusing anonymous access. Do NOT retry the same failing command; switch to an unauthenticated endpoint.
- The unauthenticated REST endpoints (`/repos/<owner>/<repo>`, `/repos/<owner>/<repo>/contents/<path>`, `/repos/<owner>/<repo>/git/trees`) work for **public** repos only. Private repos require credentials.
- A `404` on the REST API means the repo or branch genuinely does not exist — verify the owner/repo name and default branch before proceeding.

## Procedure

1. **Read a single file.** Prefer the REST API (unauthenticated, returns base64 in `content`):

```bash
curl -sL "https://api.github.com/repos/<owner>/<repo>/contents/<path>?ref=<branch>" \
  | python -c "import sys,json,base64; d=json.load(sys.stdin); print(base64.b64decode(d['content']).decode() if 'content' in d else d['message'])"
```

2. **Clone the whole repo.** Use the static tarball endpoint (no auth, no SSH handshake):

```bash
curl -sL --max-time 60 -o /tmp/repo.tar.gz "https://codeload.github.com/<owner>/<repo>/tar.gz/refs/heads/<branch>"
mkdir -p /tmp/repo && tar -xzf /tmp/repo.tar.gz -C /tmp/repo --strip-components=1
```

3. **List a repo's file tree** (to find the right path before downloading):

```bash
curl -sL "https://api.github.com/repos/<owner>/<repo>/git/trees/<branch>?recursive=1" \
  | python -c "import sys,json; d=json.load(sys.stdin); [print(t['path']) for t in d.get('tree',[])] if 'tree' in d else print(d.get('message'))"
```

4. **Search for repos** (to find a skill/tool you don't yet know the owner of):

```bash
curl -sL "https://api.github.com/search/repositories?q=<keywords>&sort=stars&per_page=10" \
  | python -c "import sys,json; d=json.load(sys.stdin); [print('-', r['full_name'], r.get('description')) for r in d.get('items',[])]"
```

Note: `/search/repositories` works unauthenticated; `/search/code` requires authentication and returns `401`.

## Pitfalls

- **tarball download can fail silently with a small body.** A `404`/`Not Found` or a 14-byte `404: Not Found` payload means the download failed — check the byte size and the first bytes before extracting, rather than assuming the archive is valid. A 14-byte file is an error, not a tarball.
- **Don't pipe curl directly to an interpreter without verifying.** Download the raw bytes to a file first, inspect them, then decode — piping `curl | python` executes untrusted content blind. Prefer the two-step form above.
- **Default branch may not be `main`.** Use the tarball's `refs/heads/<branch>` with the repo's actual default branch (check the repo root via `/repos/<owner>/<repo>` → `default_branch`).

## Verification

- Confirm the downloaded file is the expected content (size > expected, decodes without error) before using it.
- For a clone, confirm the expected files exist under the extracted directory before proceeding.
