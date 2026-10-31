import argparse
import json
import sys

import backend_windows as bw
from common import parse_value, size_of, unpack
from guard import GuardError, verify

MODES = ["exact", "changed", "unchanged", "increased", "decreased"]


def keep(mode, old, new, target):
    if mode == "exact":
        return new == target
    if mode == "changed":
        return new != old
    if mode == "unchanged":
        return new == old
    if mode == "increased":
        return new > old
    return new < old


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("state")
    parser.add_argument("mode", choices=MODES)
    parser.add_argument("--value")
    args = parser.parse_args()

    with open(args.state, encoding="utf-8") as handle_in:
        state = json.load(handle_in)

    try:
        verify(state["pid"])
    except GuardError as error:
        print("REFUSED:", error)
        sys.exit(2)

    type_name = state["type"]
    width = size_of(type_name)
    target = parse_value(type_name, args.value) if args.value is not None else None
    if args.mode == "exact" and target is None:
        print("exact mode needs --value")
        sys.exit(1)

    handle = bw.open_process(state["pid"])
    survivors = []
    try:
        for item in state["results"]:
            raw = bw.read(handle, item["addr"], width)
            if not raw or len(raw) < width:
                continue
            current = unpack(type_name, raw)
            if keep(args.mode, item["value"], current, target):
                survivors.append({"addr": item["addr"], "value": current})
    finally:
        bw.close(handle)

    state["results"] = survivors
    with open(args.state, "w", encoding="utf-8") as handle_out:
        json.dump(state, handle_out)
    print(len(survivors), "addresses left")
    for item in survivors[:20]:
        print(hex(item["addr"]), item["value"])


if __name__ == "__main__":
    main()
