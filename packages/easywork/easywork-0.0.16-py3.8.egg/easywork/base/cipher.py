import base64

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad


class Cipher:
    def __init__(self, secret):
        self.secret = secret
        self.factory = AES.new(bytes(self.secret, encoding='utf8'), AES.MODE_ECB)

    def encrypt(self, text):
        text = self.factory.encrypt(pad(bytes(text, encoding='utf8'), 32))
        return str(base64.b64encode(text), encoding='utf-8')

    def decrypt(self, data):
        data = self.factory.decrypt(base64.b64decode(data))
        return bytes.decode(unpad(data, 32))
