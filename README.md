# anticheat-lab

A Claude skill for tamper-testing **your own** game builds before release. It finds values that are exposed in process memory, then produces server-side validation fixes and regression tests. It also has an RPA mode for automating third-party Windows apps without touching their memory.

> Status: testing. The Windows backend has only been compile-checked so far. Android and iOS backends are not implemented yet.

## Modes

**Mode A: memory tamper testing (your own build only)**
Scan for values such as health, ammo or currency, narrow the results, read them, and report which ones the client exposes. Every finding comes with a defense recommendation and a regression test.

**Mode B: RPA for third-party apps**
No memory access. Preference order: the app's own export or API, then UI Automation (`pywinauto`), then OCR.

## Safety model

- Mode A only works on a process whose executable has a `devbuild.json` manifest next to it with a matching SHA-256.
- You create the manifest yourself and confirm you own the build:
  ```
  python scripts/guard.py create path\to\game.exe
  ```
- If the guard refuses, the scripts stop. Do not use this on live or online sessions, on processes protected by an anti-cheat service, or on software you do not own.
- The guard is a safety rail for the AI workflow, not a security boundary. You are responsible for how you use this.

## Install

1. Copy the repo folder to `~/.claude/skills/anticheat-lab/` (on Windows: `C:\Users\<you>\.claude\skills\anticheat-lab\`). `SKILL.md` must sit directly inside it.
2. Install Python 3. For RPA mode: `pip install pywinauto`.
3. Restart Claude Code and check that `anticheat-lab` appears in `/skills`.

## Usage

Memory testing on your own build:

```
python scripts/guard.py create C:\dev\mygame.exe
python scripts/scan.py <pid> int32 100
python scripts/next_scan.py scan_state.json exact --value 93
python scripts/rw.py read <pid> 0x1A2B3C4D int32
```

Or just ask Claude Code:

> Use the anticheat-lab skill. This is my own build (PID: 1234), the manifest is ready. Find the health value, then write the findings with defenses and regression tests.

RPA mode:

> Use the anticheat-lab skill. Write an RPA script for Windows Calculator that multiplies 12 by 30 and reads the result. No memory scanning.

## Layout

```
SKILL.md
scripts/      scan, next_scan, rw, guard, backend_windows, rpa_inspect
references/   defense.md, rpa.md
```

## Defense priorities

1. Server authority over all game state
2. Server-side validation of impossible deltas
3. Telemetry anomaly detection
4. Integrity signals
5. Client-side obfuscation (a speed bump only)

## License

MIT
