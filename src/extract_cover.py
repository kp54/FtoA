# カバーアート抽出するやつ

import argparse
from pathlib import Path
from typing import List, Tuple
import typing

import ffmpeg
import taglib

import dirtree

T = typing.TypeVar("T")


def assert_not_none(obj: T | None) -> T:
    if obj is None:
        raise RuntimeError
    return obj


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("src", type=Path, help="source directory")
    parser.add_argument("dest", type=Path, help="destination directory")

    return parser.parse_args()


def get_album_name(path: Path) -> Tuple[str, None] | Tuple[None, Exception]:
    fp = None
    try:
        fp = taglib.File(path.as_posix())
        return (fp.tags["ALBUM"][0], None)
    except OSError as err:
        return (None, err)
    finally:
        if fp:
            fp.close()


def sanitize(name: str) -> str:
    blacklist = ("\\", "/", ":", "*", "?", '"', "<", ">", "|")

    for i in blacklist:
        name = name.replace(i, "_")

    return name


def extract_cover(srcfile: Path, destdir: Path, name: str) -> Exception | None:
    destpath = destdir.joinpath(f"{name}_%02d.png")

    try:
        ffmpeg.input(srcfile.as_posix()).output(
            destpath.as_posix(),
            map="0:v",
            vcodec="png",
            loglevel="error",
        ).run()
    except ffmpeg.Error as err:
        return err

    return None


def process_tree(srcroot: Path, dest: Path) -> None:
    if not dest.exists():
        raise FileNotFoundError(dest)
    if not dest.is_dir():
        raise NotADirectoryError(dest)

    errors: List[str] = []
    processed_albums: List[str] = []

    def process(src: Path) -> None:
        rel_src = src.relative_to(srcroot)

        if not src.is_file():
            return

        album_name, err = get_album_name(src)
        if err is not None:
            print(err)
            errors.append(rel_src.as_posix())
            return

        # err が None の場合 album_name は None ではない
        sanitized_album_name = sanitize(assert_not_none(album_name))

        if sanitized_album_name in processed_albums:
            print(f"skipping: {rel_src.as_posix()}")
            return

        print(f"processing: {rel_src.as_posix()}")

        if (err := extract_cover(src, dest, sanitized_album_name)) is not None:
            print(err)
            errors.append(rel_src.as_posix())
            return

        processed_albums.append(sanitized_album_name)

    dirtree.walk(srcroot, process)

    if errors:
        print("\nerrors:\n" + "\n".join(errors))


def main() -> int:
    args = parse_args()

    process_tree(args.src, args.dest)

    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
