import hashlib
import json
import os
import sys


class GuardError(Exception):
    pass


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def manifest_path(exe):
    return os.path.join(os.path.dirname(exe), "devbuild.json")


def verify(pid):
    from backend_windows import image_path

    exe = image_path(pid)
    path = manifest_path(exe)
    if not os.path.isfile(path):
        raise GuardError("no devbuild.json next to " + exe)
    with open(path, encoding="utf-8") as handle:
        data = json.load(handle)
    if data.get("devbuild") is not True:
        raise GuardError("devbuild flag is not true")
    if str(data.get("sha256", "")).lower() != sha256_file(exe):
        raise GuardError("executable hash does not match the manifest")
    return exe


def create(exe):
    exe = os.path.abspath(exe)
    if not os.path.isfile(exe):
        raise GuardError("file not found: " + exe)
    answer = input("Confirm you own and built " + exe + " (type yes): ")
    if answer.strip().lower() != "yes":
        raise GuardError("not confirmed")
    with open(manifest_path(exe), "w", encoding="utf-8") as handle:
        json.dump({"devbuild": True, "sha256": sha256_file(exe)}, handle, indent=2)
    print("manifest written")


if __name__ == "__main__":
    try:
        if len(sys.argv) == 3 and sys.argv[1] == "create":
            create(sys.argv[2])
        elif len(sys.argv) == 3 and sys.argv[1] == "check":
            print("OK", verify(int(sys.argv[2])))
        else:
            print("usage: guard.py create <exe> | check <pid>")
            sys.exit(1)
    except GuardError as error:
        print("REFUSED:", error)
        sys.exit(2)
