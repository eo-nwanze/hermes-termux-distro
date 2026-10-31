---
name: local-memory
description: Local persistent memory for Hermes Agent — store and recall facts, preferences, and notes on device without cloud services
triggers:
  - remember this
  - save note
  - local notes
  - recall
  - save fact
  - local memory
  - note taking
---

# Local Memory (Samsung Fold 7)

Local persistent memory for storing and recalling facts, preferences, and notes on device. No cloud dependency.

## Memory Locations

```
~/notes/              # General notes (plain text)
~/notes/facts/        # Facts and knowledge
~/notes/preferences/  # User preferences
~/notes/projects/     # Project-specific notes
~/notes/daily/        # Daily journals
```

## Quick Commands

### Store a Note

```bash
# Quick note
echo "$(date +%Y-%m-%d): This is my note" >> ~/notes/quick.md

# Categorized note
mkdir -p ~/notes/facts
echo "- Python is preferred language" >> ~/notes/facts/preferences.md

# Daily journal
mkdir -p ~/notes/daily
cat >> ~/notes/daily/$(date +%Y-%m-%d).md << 'EOF'
## $(date +%H:%M)
- Did something important
- Need to follow up on X
EOF
```

### Search Notes

```bash
# Search all notes
grep -rn "search term" ~/notes/

# Search specific category
grep -rn "term" ~/notes/facts/

# List today's notes
cat ~/notes/daily/$(date +%Y-%m-%d).md
```

### Recall with Hermes

The Hermes `memory` tool is the primary way to store persistent facts:

- **User preferences**: `memory(action='add', target='user', content='prefers dark mode')`
- **Agent notes**: `memory(action='add', target='memory', content='project X uses port 8080')`
- These persist across sessions automatically

### Project Notes Template

```markdown
# Project: [Name]
- Created: YYYY-MM-DD
- Status: active/paused/done

## Key Facts
- ...

## TODO
- [ ] ...

## Decisions
- ...
```

## Samsung Fold 7 Tips

- Store notes on internal storage (`~/notes/`) for speed
- Use `/storage/emulated/0/Notes/` for notes visible in gallery/files app
- Sync with Git for backup: `cd ~/notes && git init && git remote add origin ...`
- When unfolded, use split-screen: notes on one side, terminal on the other

## Integration with Hermes Memory

Use both systems together:
1. **Hermes memory tool** for quick facts/preferences (auto-injected into sessions)
2. **Local files** for long-form notes, documentation, journals
3. **Obsidian vault** (see obsidian skill) for linked knowledge graphs