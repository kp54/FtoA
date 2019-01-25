# カバーアート抽出するやつ

import os
import os.path
import ffmpeg
import taglib


def extract(src, dest):
    que = os.listdir(src)
    psd = list()
    err = list()

    abs_d = os.path.join(dest, 'cover/')
    if not os.path.exists(abs_d):
        os.mkdir(abs_d)

    while que:
        rel = que.pop()
        abs_s = os.path.join(src, rel)

        if os.path.isdir(abs_s):
            print(f'scanning: {rel}')

            try:
                que.extend(map(lambda x: os.path.join(rel, x), os.listdir(abs_s)))
            except PermissionError:
                print(f'permission error: {rel}')

        elif os.path.isfile(abs_s):
            try:
                fp = taglib.File(abs_s)
                alb = fp.tags['ALBUM'][0]
            finally:
                fp.close()

            if alb in psd:
                print(f'skipping: {rel}')
                continue
            psd.append(alb)

            print(f'processing: {rel}')
            abs_d = os.path.join(dest, f'cover/{alb.replace("/", "_")}_%02d.png')

            try:
                ffmpeg.input(abs_s).output(abs_d, map='0:v', vcodec='png', loglevel='error').run()
            except ffmpeg.Error:
                err.append(abs_s)

    print('\nerror:\n'+'\n'.join(err))

    return


def main():
    SRC = '/path/to/source/'
    DEST = '/path/to/destination/'

    extract(SRC, DEST)

    return 0


if __name__ == '__main__':
    import sys

    sys.exit(main())
