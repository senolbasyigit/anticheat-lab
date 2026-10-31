# RPA mode

No memory scanning of third-party apps. Addresses change on every update and the data is often sensitive.

## Selection

1. Export or API: CSV, Excel, XML, database access, COM. Check the app's documentation first.
2. UI Automation with `pywinauto` (`backend="uia"`): find controls by name, control type or automation id, never by pixel position.
3. OCR or image matching only if the control tree is empty (custom-drawn UI).

## Procedure

1. Run `scripts/rpa_inspect.py` on the target window and save the tree.
2. Map each needed value or field to a control identifier.
3. Write the automation with explicit waits, retries, timeouts, structured logging.
4. Include `--dry-run` that reads and reports but does not write.
5. Test on a copy of the data. Ask the user before any write to real records.
6. Keep identifiers in one config block so app updates need a one-line fix.
