# 5072

A small Python checker for Git commit messages that enforces the **50/72 rule**:

- **50**: the subject line (the first line Git keeps) is at most 50 characters so one-line summaries stay readable in logs and `git log --oneline`.
- **72**: every following line is at most 72 characters so wrapped text fits common terminals and tools.

Comment lines (optional leading whitespace, then `#`) are ignored, consistent with how Git strips them from the final message.

## Requirements

- Python 3.9+ (uses `list[str]` typing; adjust if you need older Python)

## Why `commit-msg`, not `pre-commit`?

Git’s **`pre-commit`** hook runs before the commit is recorded and does not receive the final message file the same way. Message checks belong on the **`commit-msg`** hook, which receives the path to the proposed log message as the first argument.

If you use the [pre-commit](https://pre-commit.com/) framework, register this script on the **`commit-msg` stage** (see below).

## Commit message template (50/72 reminder)

This repo includes [`.gitmessage`](.gitmessage): when you run `git commit`, your editor can open with a short checklist (as commented lines Git strips out). Point Git at it from the repository root:

```sh
git config commit.template .gitmessage
```

Or set it only for this clone: `git config --local commit.template .gitmessage`.

## Install as a Git `commit-msg` hook

From your repository root (adjust the path if you move the script):

```sh
mkdir -p .git/hooks
cat > .git/hooks/commit-msg <<'EOF'
#!/bin/sh
exec python3 "$(git rev-parse --show-toplevel)/5072.py" "$1"
EOF
chmod +x .git/hooks/commit-msg
```

To share hooks with the team, use [core.hooksPath](https://git-scm.com/docs/git-config#Documentation/git-config.txt-corehooksPath) pointing at a versioned `hooks/` directory and commit a `commit-msg` wrapper there.

## Install with the pre-commit framework

Add to `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: local
    hooks:
      - id: commit-msg-50-72
        name: 50/72 commit message
        entry: python3 5072.py
        language: system
        stages: [commit-msg]
        always_run: true
```

Then run `pre-commit install --hook-type commit-msg`.

## Example message

```
Add retry backoff for API client

When the upstream returns 429, sleep using Retry-After before
retrying. Keeps logs quieter and avoids hammering the service.
```

The first line is the subject (≤ 50 characters). A blank line separates the body; each body line should be ≤ 72 characters.

## Manual check

```sh
printf '%s\n' 'Short subject' > /tmp/msg.txt
python3 5072.py /tmp/msg.txt && echo OK
```

The script exits `0` if the message is valid and `1` if not, printing details to stderr.
