# Windowsの禁則文字に対応するやつ

import argparse
from pathlib import Path
from typing import List

import dirtree


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path, help="root directory for process")

    return parser.parse_args()


def replace_forbidden_character(filename: str) -> str:
    forbidden = ("\\", "/", ":", "*", "?", '"', "<", ">", "|")

    for i in forbidden:
        filename = filename.replace(i, "_")

    return filename


def rename(src: Path, dest: Path) -> Exception | None:
    try:
        src.rename(dest)
    except PermissionError as err:
        return err

    return None


def process_tree(root: Path) -> None:
    errors: List[str] = []

    def process(path: Path) -> None:
        rel_path = path.relative_to(root)

        if not path.is_file():
            return

        new_name = replace_forbidden_character(path.name)

        if (err := rename(path, path.with_name(new_name))) is not None:
            print(err)
            errors.append(rel_path.as_posix())
            return

    dirtree.walk(root, process)

    if len(errors) != 0:
        print("\nerrors:\n" + "\n".join(errors))


def main() -> int:
    args = parse_args()

    process_tree(args.root)

    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
