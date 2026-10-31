# Defense guide

Priority order for every finding:

1. Server authority: the server owns health, ammo, currency, inventory, cooldowns, position. The client sends intent, never state.
2. Server-side validation: reject impossible deltas (speed over max, damage over weapon cap, fire rate over cooldown, currency gain without a source event).
3. Telemetry anomaly detection: per-session statistics on rates and deltas, flagged for review rather than auto-banned until tuned.
4. Integrity signals: build signature checks, debugger and tamper detection. Treat as signals feeding the server, not as proof.
5. Client-side value obfuscation (encrypted or split values, shadow copies): slows scanning, never relied on alone.

## Finding format

- Title
- Value and where it lives
- How it was located (scan steps)
- Client authoritative? Server revalidates?
- Impact
- Fix (ordered as above)
- Regression test name and what it asserts

## Regression test patterns

- Send a state update with an impossible delta and assert the server rejects it and logs an event.
- Replay a recorded session with one tampered value and assert the anomaly detector flags it.
- Assert the client never sends absolute values for server-owned fields.
