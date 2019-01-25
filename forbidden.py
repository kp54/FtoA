# Windowsの禁則文字に対応するやつ

import os
import os.path


def _rename(src):
    forbidden = ('\\', '/', ':', '*', '?', '"', '<', '>', '|')

    path, target = os.path.split(src)

    for i in forbidden:
        target = target.replace(i, '_')

    dest = os.path.join(path, target)
    os.rename(src, dest)

    return dest


def rename(target):
    que = os.listdir(target)

    while que:
        rel = que.pop()
        abs_ = os.path.join(target, rel)
        if os.path.isdir(abs_):
            print(f'entering: {rel}')
            abs_ = _rename(abs_)
            try:
                que.extend(map(lambda x: os.path.join(rel, x), os.listdir(abs_)))
            except PermissionError:
                print(f'permission error: {rel}')

        elif os.path.isfile(abs_):
            print(f'processing {rel}')
            _rename(abs_)


def main():
    TARGET = '/path/to/target/'

    rename(TARGET)

    return 0


if __name__ == '__main__':
    import sys

    sys.exit(main())
