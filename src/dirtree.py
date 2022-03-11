import os
from pathlib import Path
from typing import Any, Callable


def walk(root: Path, processor: Callable[[Path], Any]) -> None:
    if not root.exists():
        raise FileNotFoundError(root)
    if not root.is_dir():
        raise NotADirectoryError(root)

    for (str_current, directories, files) in os.walk(root):
        current = Path(str_current)

        for i in files + directories:
            path = current.joinpath(i)
            processor(path)


def mirror(
    srcroot: Path,
    destroot: Path,
    processor: Callable[[Path, Path], Any] | None = None,
) -> None:
    if not srcroot.exists():
        raise FileNotFoundError(srcroot)
    if not srcroot.is_dir():
        raise NotADirectoryError(srcroot)
    if not destroot.exists():
        raise FileNotFoundError(destroot)
    if not destroot.is_dir():
        raise NotADirectoryError(destroot)

    def process(src: Path) -> None:
        rel_src = src.relative_to(srcroot)
        dest = destroot.joinpath(rel_src)

        if src.is_file() and processor is not None:
            processor(src, dest)

        if src.is_dir() and not dest.exists():
            dest.mkdir()

    walk(srcroot, process)


def main() -> None:
    import shutil
    import sys

    if len(sys.argv) < 3:
        print(f"usage: {sys.argv[0]} src dest")
        return

    mirror(Path(sys.argv[1]), Path(sys.argv[2]), shutil.copy2)


if __name__ == "__main__":
    main()
