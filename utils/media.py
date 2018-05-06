import os

import binascii


def generate_path_to_file(media_root, upload_to, *args):
    if not os.path.exists(media_root):
        os.mkdir(media_root)

    path = media_root
    if upload_to is not None:
        path = '{}/{}'.format(path, upload_to)
        if not os.path.exists(path):
            os.mkdir(path)

    for arg in args:
        if not isinstance(arg, str):
            arg = str(arg)

        path = '{}/{}'.format(path, arg)
        if not os.path.exists(path):
            os.mkdir(path)

    return path


def generate_file_name(path, filename):
    path_to_file = '{}/{}'.format(path, filename)
    while os.path.exists(path_to_file):
        filename = '{}_{}'.format(binascii.hexlify(os.urandom(5)).decode(), filename)
        path_to_file = '{}/{}'.format(path, filename)

    return filename
