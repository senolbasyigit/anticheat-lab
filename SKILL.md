---
name: anticheat-lab
description: Tamper-test the user's OWN game or app build for memory-editing cheats, then produce defenses (server-side validation, anomaly detection) and regression tests. Also provides an RPA mode for automating third-party Windows apps through exports, APIs and UI Automation. Use whenever the user mentions cheat testing, anti-cheat, memory scanning, Cheat Engine style testing of their own build, reverse engineering their own game, hardening a game before release, or automating a desktop app (accounting software, ERP, legacy tools) with macros or RPA, even if they do not use those exact words.
---

# anticheat-lab

Two modes. Pick one before doing anything else.

- Mode A: memory tamper testing of a build the user owns, followed by defenses.
- Mode B: RPA for third-party apps. No memory access in this mode.

## Hard rules

1. Mode A runs only against a process whose executable has a `devbuild.json` manifest next to it with a matching SHA-256. `scripts/guard.py` enforces this and every script calls it.
2. The user creates the manifest themselves with `python scripts/guard.py create <exe>`, which asserts they own the build. Never run `create` on the user's behalf and never write a manifest yourself.
3. If the guard refuses, stop and tell the user why. Do not edit the guard, bypass it, or reach for another scanner or debugger.
4. Never touch live or online game sessions, processes protected by an anti-cheat service, or any process that is not the verified dev build.
5. Never use memory access on third-party applications. Use Mode B.
6. Writes to memory are only for demonstrating that a tampered value is rejected. Use `rw.py write --confirm-dev-build` and record the result.

## Mode A workflow

1. Ask for engine, platform, and which values matter (health, ammo, currency, score, position, cooldowns). Confirm the build is theirs and the guard manifest exists.
2. Scan: `python scripts/scan.py <pid> int32 <value>` then change the value in game and run `python scripts/next_scan.py <state.json> exact --value <new>` (modes: exact, changed, unchanged, increased, decreased) until a handful of addresses remain.
3. Read the address with `rw.py read`. Optionally write a tampered value to see whether the game, and more importantly the server, accepts it.
4. For each exposed value write a finding: value, how it was located, whether the client is authoritative, whether the server revalidates, impact.
5. Read `references/defense.md` and attach defenses to each finding. Server-side validation comes first; client-side obfuscation is only a speed bump and must be labeled that way.
6. Generate a regression test per finding (server rejects the impossible state, telemetry flags it) in the user's own test framework.
7. Produce the report using the format in `references/defense.md`.

## Platforms

- Windows: implemented in `scripts/backend_windows.py`.
- Android and iOS: not implemented yet. A backend must expose the same functions as `backend_windows.py` (`open_process`, `regions`, `read`, `write`, `image_path`). Android requires a `debuggable` build, iOS a dev-signed build with `get-task-allow`. Reject anything else, same as the guard does on Windows.
- Linux: same interface via `/proc/<pid>/mem`, same guard requirement.

## Mode B workflow (RPA)

Read `references/rpa.md`. Order of preference:

1. The app's own exports, database, API or COM interface.
2. UI Automation: `python scripts/rpa_inspect.py "<window title regex>"` dumps the control tree; use names and automation ids to build the script.
3. OCR and image matching as a last resort.

Generated automations must include waits for controls, error handling, a dry-run flag, logging, and must run first against a copy of the data. Ask before writing into any accounting or financial record.
