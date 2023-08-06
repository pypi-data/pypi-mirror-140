import socket
import uuid
from contextlib import closing


def mac():
    return uuid.UUID(int=uuid.getnode()).hex[-12:]


def get_free_port():
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]


def port_is_used(port: int):
    assert port in range(0, 65535)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('127.0.0.1', port))
        s.shutdown(2)
        return True
    except:
        return False
