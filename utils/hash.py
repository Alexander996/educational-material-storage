import hashlib

import binascii

import os


def hash_password(password):
    t_sha = hashlib.sha256()
    t_sha.update(password.encode('utf-8'))
    password = t_sha.hexdigest()
    return password


def generate_token():
    return binascii.hexlify(os.urandom(20)).decode()
