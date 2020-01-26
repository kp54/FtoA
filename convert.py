# flacをalacに変換するやつ

import argparse
import os
import os.path

import ffmpeg


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('src', help='source directory')
    parser.add_argument('out', help='output directory')

    return parser.parse_args()


def convert(src, dest):
    que = os.listdir(src)
    err = list()

    while que:
        rel = que.pop()
        abs_s = os.path.join(src, rel)
        abs_d = os.path.join(dest, rel)

        if os.path.isdir(abs_s):
            if os.path.exists(abs_d):
                print(f'skipping: {rel}')
                continue
            os.mkdir(abs_d)
            print(f'scanning: {rel}')

            try:
                que.extend(map(lambda x: os.path.join(rel, x), os.listdir(abs_s)))
            except PermissionError:
                print(f'permission error: {rel}')

        elif os.path.isfile(abs_s):
            print(f'processing: {rel}')
            abs_d = os.path.splitext(abs_d)[0]+'.m4a'

            try:
                ffmpeg.input(abs_s).output(abs_d, acodec='alac', vcodec='png', loglevel='error').run()
            except ffmpeg.Error:
                err.append(abs_s)

    print('\nerror:\n'+'\n'.join(err))

    return


def main():
    args = parse_args()

    convert(args.src, args.out)

    return 0


if __name__ == '__main__':
    import sys

    sys.exit(main())
