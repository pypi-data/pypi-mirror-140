import random


def get_hanzi(size: int = 3):
    result = ''
    for _ in range(size):
        result += chr(random.randint(0x4e00, 0x9fbf))
    return result


def get_secret(size: int = 16):
    return ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789', k=size))
