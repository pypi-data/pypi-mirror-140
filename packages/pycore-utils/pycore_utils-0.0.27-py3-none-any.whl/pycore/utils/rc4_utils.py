# 加密
import base64
from Crypto.Cipher import ARC4

from pycore.utils.stringutils import StringUtils


def new_keys(length):
    return StringUtils.randomStr(length)


# 解密
def rc4_decode(data: str, key: str):
    rc41 = ARC4.new(key.encode('utf-8'))
    return rc41.decrypt(base64.b64decode(data.encode('utf-8'))).decode("utf8")


# 加密
def rc4_encode(data: str, key: str):
    rc41 = ARC4.new(key.encode('utf-8'))
    return base64.b64encode(rc41.encrypt(data.encode('utf-8'))).decode('utf-8').replace('\n', '')  # 加密
