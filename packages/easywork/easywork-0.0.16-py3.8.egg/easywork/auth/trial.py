from enum import Enum

from easywork.api.timezone import get_beijing_time
from easywork.base.cipher import Cipher
from easywork.util.native import mac
from easywork.util.steganography import decode_image
from easywork.util.time import differ_days, now, strptime


class Role(Enum):
    admin = '正式版'
    user = '卡密版'
    visitor = '试用版'


class Trial:
    def __init__(self, expire, secret, logo_path):
        self.expire = expire
        self.secret = secret
        self.logo_path = logo_path
        self.remaining_days = 0
        self.role = self.check()

    def check(self):
        try:
            logo_secret = Cipher(self.secret).decrypt(decode_image(self.logo_path))
            if logo_secret == self.secret:
                return Role.admin
            logo_secret_arr = logo_secret.split('_')
            if logo_secret_arr[0] == mac():
                self.remaining_days = self.get_remaining_days(logo_secret_arr[1])
                self.expire = logo_secret_arr[1]
                return Role.user
        except:
            return Role.visitor

    def get_remaining_days(self, expire_time=None):
        if not expire_time:
            expire_time = self.expire
        expire_time = strptime(expire_time, '%Y年%m月%d日')
        current_time = get_beijing_time()
        if not current_time:
            current_time = now()
        return max(differ_days(expire_time, current_time), 0)
