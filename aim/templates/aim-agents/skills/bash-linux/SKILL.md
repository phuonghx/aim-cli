---
name: bash-linux
description: A working reference for the Bash shell on Linux and macOS. Covers command chaining, file and process handling, text pipelines, scripting scaffolds, and safe error handling. Useful whenever shell work happens on a Unix-like machine instead of Windows.
---

# Working in Bash on Unix Systems

A condensed field guide to getting things done in a POSIX shell.

---

## 1. Stringing Commands Together

The shell glues commands with a handful of operators. Pick the one that matches the relationship you want between steps.

| Symbol | Behavior | Sample |
|--------|----------|--------|
| `;` | Always run the next one | `make clean; make` |
| `&&` | Continue only on success | `go build && ./app` |
| `\|\|` | React only to failure | `ping -c1 host \|\| echo unreachable` |
| `\|` | Feed stdout into the next command | `cat access.log \| grep 404` |

---

## 2. Touching the Filesystem

| Goal | Command |
|------|---------|
| Detailed listing | `ls -lah` |
| Locate by name | `find . -type f -name '*.py'` |
| Dump a file | `cat config.yaml` |
| Top of a file | `head -n 30 report.txt` |
| Bottom of a file | `tail -n 30 report.txt` |
| Stream new lines | `tail -f server.log` |
| Recursive text hunt | `grep -rn 'TODO' --include='*.go' .` |
| Size of entries | `du -sh ./*` |
| Free space | `df -h` |

---

## 3. Watching and Steering Processes

| Goal | Command |
|------|---------|
| Snapshot everything | `ps aux` |
| Filter by program | `pgrep -fl python` |
| Terminate by id | `kill -TERM <pid>` (escalate to `-9` only if stuck) |
| Who holds a port | `lsof -i :8080` |
| Free a port | `kill $(lsof -t -i :8080)` |
| Detach a job | `./worker &` |
| List background jobs | `jobs -l` |
| Resume in foreground | `fg %1` |

---

## 4. Reshaping Text

| Utility | Role | Sample |
|---------|------|--------|
| `grep` | Match lines | `grep -i 'error' app.log` |
| `sed` | Stream-edit | `sed -i 's/staging/prod/g' env.conf` |
| `awk` | Field logic | `awk -F: '{print $1}' /etc/passwd` |
| `cut` | Slice columns | `cut -d, -f2 sales.csv` |
| `sort` | Order lines | `sort -n nums.txt` |
| `uniq` | Collapse repeats | `sort names.txt \| uniq -c` |
| `tr` | Translate chars | `tr 'a-z' 'A-Z' < in.txt` |
| `wc` | Tally | `wc -l data.txt` |

---

## 5. Environment Variables

| Goal | Command |
|------|---------|
| Dump all | `printenv` |
| Read one | `echo "$HOME"` |
| Export for the session | `export API_KEY='abc123'` |
| Scope to one command | `LOG_LEVEL=debug ./run.sh` |
| Extend PATH | `export PATH="/opt/bin:$PATH"` |

---

## 6. Talking to the Network

| Goal | Command |
|------|---------|
| Save a download | `curl -fSL -O https://host/pkg.tar.gz` |
| Plain GET | `curl https://api.host/status` |
| POST a payload | `curl -X POST -H 'Content-Type: application/json' -d '{"id":7}' https://api.host/items` |
| Probe a port | `nc -zv db.host 5432` |
| Inspect interfaces | `ip addr` (or `ifconfig` on older systems) |

---

## 7. A Starter Script

```bash
#!/usr/bin/env bash
set -euo pipefail   # stop on errors, unset vars, and broken pipes

# Resolve where this script lives, regardless of caller's cwd
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Tiny logging helpers
say()  { printf '\033[0;32m[ok]\033[0m %s\n' "$1"; }
warn() { printf '\033[0;31m[!!]\033[0m %s\n' "$1" >&2; }

run() {
    say "kicking off in $here"
    # real work goes here
    say "finished"
}

run "$@"
```

---

## 8. Patterns Worth Memorizing

Confirm a binary is present before using it:

```bash
if command -v docker >/dev/null 2>&1; then
    warn() { :; }   # docker exists, proceed
fi
```

Fall back to a default argument:

```bash
target="${1:-./build}"
```

Walk a file one line at a time:

```bash
while IFS= read -r entry; do
    printf 'got: %s\n' "$entry"
done < hosts.txt
```

Iterate over matching files:

```bash
for src in ./*.css; do
    printf 'minifying %s\n' "$src"
done
```

---

## 9. Coming from PowerShell?

| Task | PowerShell | Bash |
|------|------------|------|
| List directory | `Get-ChildItem` | `ls -lah` |
| Recursive find | `Get-ChildItem -Recurse` | `find . -type f` |
| Read env var | `$env:PATH` | `$PATH` |
| Join strings | `"$a$b"` | `"$a$b"` |
| Test non-empty | `if ($x)` | `[ -n "$x" ]` |
| Pipeline carries | Objects | Plain text |

The biggest mental shift: PowerShell pipes objects, Bash pipes raw bytes. Quote variables so word-splitting doesn't surprise you.

---

## 10. Failing Safely

Turn on guard rails at the top of any non-trivial script:

```bash
set -e          # bail on the first failing command
set -u          # treat unset variables as errors
set -o pipefail # a failure anywhere in a pipe fails the whole pipe
set -x          # echo each command (handy while debugging)
```

Guarantee cleanup even when something blows up:

```bash
workdir="$(mktemp -d)"
finish() { rm -rf "$workdir"; }
trap finish EXIT
```

---

> **Takeaway:** chain with `&&` when each step depends on the last, enable `set -euo pipefail` for safety, and always wrap variables in quotes.
