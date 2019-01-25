# flacをalacに変換するやつ

import os
import os.path
import ffmpeg


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
                ffmpeg.input(abs_s).output(abs_d, map='0:a', acodec='alac', loglevel='error').run()
            except ffmpeg.Error:
                err.append(abs_s)

    print('\nerror:\n'+'\n'.join(err))

    return


def main():
    SRC = '/path/to/source/'
    DEST = '/path/to/destination/'

    convert(SRC, DEST)

    return 0


if __name__ == '__main__':
    import sys

    sys.exit(main())
