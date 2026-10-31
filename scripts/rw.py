import argparse
import sys

import backend_windows as bw
from common import pack, parse_value, size_of, unpack
from guard import GuardError, verify


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)
    read = sub.add_parser("read")
    write = sub.add_parser("write")
    for item in (read, write):
        item.add_argument("pid", type=int)
        item.add_argument("addr")
        item.add_argument("type", choices=["int32", "float", "double"])
    write.add_argument("value")
    write.add_argument("--confirm-dev-build", action="store_true")
    args = parser.parse_args()

    try:
        verify(args.pid)
    except GuardError as error:
        print("REFUSED:", error)
        sys.exit(2)

    address = int(args.addr, 0)
    if args.cmd == "read":
        handle = bw.open_process(args.pid)
        try:
            raw = bw.read(handle, address, size_of(args.type))
        finally:
            bw.close(handle)
        if not raw or len(raw) < size_of(args.type):
            print("read failed")
            sys.exit(1)
        print(unpack(args.type, raw))
        return

    if not args.confirm_dev_build:
        print("write needs --confirm-dev-build")
        sys.exit(1)
    handle = bw.open_process(args.pid, write=True)
    try:
        ok = bw.write(handle, address, pack(args.type, parse_value(args.type, args.value)))
    finally:
        bw.close(handle)
    print("written" if ok else "write failed")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
