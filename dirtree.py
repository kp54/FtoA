import os
from pathlib import Path
from typing import Any, Callable


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

    for (strsrccwd, directories, files) in os.walk(srcroot):
        srccwd = Path(strsrccwd)
        relativecwd = srccwd.relative_to(srcroot)
        destcwd = destroot.joinpath(relativecwd)

        for i in files:
            srcpath = srccwd.joinpath(i)
            destpath = destcwd.joinpath(i)

            if processor is None:
                continue

            processor(srcpath, destpath)

        for i in directories:
            destpath = destcwd.joinpath(i)

            if destpath.exists():
                continue

            destpath.mkdir()


def main() -> None:
    import shutil
    import sys

    if len(sys.argv) < 3:
        print(f"usage: {sys.argv[0]} src dest")
        return

    mirror(Path(sys.argv[1]), Path(sys.argv[2]), shutil.copy2)


if __name__ == "__main__":
    main()
