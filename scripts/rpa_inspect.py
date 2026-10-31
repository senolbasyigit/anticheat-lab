import argparse
import json

from pywinauto import Desktop


def walk(element, depth, max_depth, rows):
    info = element.element_info
    rows.append(
        {
            "depth": depth,
            "control_type": info.control_type,
            "name": info.name,
            "auto_id": info.automation_id,
            "class_name": info.class_name,
        }
    )
    if depth >= max_depth:
        return
    for child in element.children():
        walk(child, depth + 1, max_depth, rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("title_regex")
    parser.add_argument("--depth", type=int, default=6)
    parser.add_argument("--out", default="control_tree.json")
    args = parser.parse_args()

    window = Desktop(backend="uia").window(title_re=args.title_regex)
    window.wait("exists", timeout=10)
    rows = []
    walk(window.wrapper_object(), 0, args.depth, rows)
    with open(args.out, "w", encoding="utf-8") as handle:
        json.dump(rows, handle, ensure_ascii=False, indent=2)
    print(len(rows), "controls saved to", args.out)


if __name__ == "__main__":
    main()
