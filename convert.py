# flacをalacに変換するやつ

import argparse
import copy
from pathlib import Path
from typing import List

import ffmpeg
import taglib

import dirtree


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("src", type=Path, help="source directory")
    parser.add_argument("dest", type=Path, help="destination directory")

    return parser.parse_args()


def convert(src: Path, dest: Path) -> bool:
    try:
        ffmpeg.input(src.as_posix()).output(
            dest.as_posix(),
            acodec="alac",
            vcodec="png",
            loglevel="error",
        ).run()
    except ffmpeg.Error as err:
        print(err)
        return False

    return True


def copy_meta(src: Path, dest: Path) -> bool:
    fp = None
    try:
        fp = taglib.File(src.as_posix())
        tags = copy.deepcopy(fp.tags)
    except OSError as err:
        print(err)
        return False
    finally:
        if fp:
            fp.close()

    try:
        tags["DISCNUMBER"][0] = f"{tags['DISCNUMBER'][0]}/{tags['DISCTOTAL'][0]}"
        tags["TRACKNUMBER"][0] = f"{tags['TRACKNUMBER'][0]}/{tags['TRACKTOTAL'][0]}"
        del tags["DISCTOTAL"]
        del tags["TRACKTOTAL"]
    except KeyError as err:
        print(err)
        return False

    fp = None
    try:
        fp = taglib.File(dest.as_posix())
        fp.tags = tags
        fp.save()
    except OSError as err:
        print(err)
        return False
    finally:
        if fp:
            fp.close()

    return True


def process_tree(srcroot: Path, destroot: Path) -> None:
    errors: List[str] = []

    def process(src: Path, dest: Path) -> None:
        rel_src = src.relative_to(srcroot)
        conv_dest = dest.with_suffix(".m4a")
        rel_conv_dest = conv_dest.relative_to(destroot)

        if src.suffix != ".flac":
            print(f"skipping non-flac file: {rel_src.as_posix()}")
            return

        if conv_dest.exists():
            print(f"skipping existing file: {rel_conv_dest.as_posix()}")
            return

        print(f"processing: {rel_src}")

        if not convert(src, conv_dest):
            errors.append(rel_src.as_posix())
            return

        if not copy_meta(src, conv_dest):
            errors.append(rel_src.as_posix())
            return

    dirtree.mirror(srcroot, destroot, process)

    if errors:
        print("\nerrors:\n" + "\n".join(errors))

    return


def main() -> int:
    args = parse_args()

    process_tree(args.src, args.dest)

    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
