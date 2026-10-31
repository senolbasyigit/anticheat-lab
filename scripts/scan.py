import argparse
import json
import sys

import backend_windows as bw
from common import TYPES, pack, parse_value, size_of
from guard import GuardError, verify

CHUNK = 1 << 20


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("pid", type=int)
    parser.add_argument("type", choices=list(TYPES))
    parser.add_argument("value")
    parser.add_argument("--out", default="scan_state.json")
    parser.add_argument("--limit", type=int, default=200000)
    args = parser.parse_args()

    try:
        verify(args.pid)
    except GuardError as error:
        print("REFUSED:", error)
        sys.exit(2)

    value = parse_value(args.type, args.value)
    needle = pack(args.type, value)
    width = size_of(args.type)
    handle = bw.open_process(args.pid)
    hits = []
    try:
        for base, region_size in bw.regions(handle):
            offset = 0
            while offset < region_size and len(hits) < args.limit:
                length = min(CHUNK, region_size - offset)
                data = bw.read(handle, base + offset, length)
                if data:
                    pos = data.find(needle)
                    while pos != -1 and len(hits) < args.limit:
                        address = base + offset + pos
                        if address % width == 0:
                            hits.append({"addr": address, "value": value})
                        pos = data.find(needle, pos + 1)
                offset += length
    finally:
        bw.close(handle)

    with open(args.out, "w", encoding="utf-8") as handle_out:
        json.dump({"pid": args.pid, "type": args.type, "results": hits}, handle_out)
    print(len(hits), "matches saved to", args.out)


if __name__ == "__main__":
    main()
