import base64
from hashlib import md5
from Crypto.Cipher import AES

BLOCK_SIZE = 16


def pad(data):
    pad = BLOCK_SIZE - len(data) % BLOCK_SIZE

    return data + pad * chr(pad)


def unpad(padded):
    pad = ord(chr(padded[-1]))

    return padded[:-pad]


def encrypt(data, password):
    m = md5()
    m.update(password.encode('utf-8'))

    key = m.hexdigest()

    m = md5()
    m.update((password + key).encode('utf-8'))

    iv = m.hexdigest()

    aes = AES.new(key.encode('utf-8'), AES.MODE_CBC, iv[:16].encode('utf-8'))
    encrypted = aes.encrypt(pad(data).encode('utf-8'))

    return base64.urlsafe_b64encode(encrypted)


def decrypt(edata, password):
    edata = base64.urlsafe_b64decode(edata)

    m = md5()
    m.update(password.encode('utf-8'))

    key = m.hexdigest()

    m = md5()
    m.update((password + key).encode('utf-8'))

    iv = m.hexdigest()
    aes = AES.new(key.encode('utf-8'), AES.MODE_CBC, iv[:16].encode('utf-8'))

    return unpad(aes.decrypt(edata)).decode('utf-8')

