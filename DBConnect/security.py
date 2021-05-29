import base64
import hashlib

from Crypto import Random
from Crypto.Cipher import AES

# from Crypto.Util.Padding import pad

BS = 16
pad = lambda s: s + (BS - len(s.encode('utf-8')) % BS) * chr(BS - len(s.encode('utf-8')) % BS)
unpad = lambda s: s[:-ord(s[len(s) - 1:])]


class AESCipher:
    def __init__(self, key):
        self.key = key

    def encrypt(self, raw):
        raw = pad(raw)
        # iv = Random.new().read(AES.block_size)
        iv = b'1234567812345678'
        iv = base64.b64encode(iv)
        # iv = iv.encode('utf-8')
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw.encode('utf-8')))

    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        iv = enc[:16]
        print(iv)
        # iv = iv.encode('utf-8')
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return unpad(cipher.decrypt(enc[16:]))


# class AESCipher1(object):
#
#     def __init__(self, key):
#         self.bs = AES.block_size
#         self.key = hashlib.sha256(key.encode()).digest()
#
#     def encrypt(self, raw):
#         raw = self._pad(raw)
#         iv = Random.new().read(AES.block_size)
#         cipher = AES.new(self.key, AES.MODE_CBC, iv)
#         return base64.b64encode(iv + cipher.encrypt(raw.encode()))
#
#     def decrypt(self, enc):
#         enc = base64.b64decode(enc)
#         iv = enc[:AES.block_size]
#         cipher = AES.new(self.key, AES.MODE_CBC, iv)
#         return self._unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')
#
#     def _pad(self, s):
#         return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)
#
#     @staticmethod
#     def _unpad(s):
#         return s[:-ord(s[len(s) - 1:])]
#
# class AesCrypt:
#     def __init__(self, model, iv, encode_, key):
#         self.encode_ = encode_
#         self.model = {'ECB': AES.MODE_ECB, 'CBC': AES.MODE_CBC}[model]
#         self.key = self.add_16(key)
#         if model == 'ECB':
#             self.aes = AES.new(self.key, self.model)  # Create an aes object
#         elif model == 'CBC':
#             self.aes = AES.new(self.key, self.model, iv)  # Create an aes object
#
#         # Here the key length must be 16, 24 or 32, and the current 16-bit is enough.
#
#     def add_16(self, par):
#         par = par.encode(self.encode_)
#         while len(par) % 16 != 0:
#             par += b'\x00'
#         return par
#
#     # encryption
#     def aesencrypt(self, text):
#         text = pad(text.encode('utf-8'), AES.block_size, style='pkcs7')
#         self.encrypt_text = self.aes.encrypt(text)
#         return base64.encodebytes(self.encrypt_text).decode().strip()
#
#     # Decrypt
#     def aesdecrypt(self, text):
#         text = base64.decodebytes(text.encode(self.encode_))
#         self.decrypt_text = self.aes.decrypt(text)
#         return self.decrypt_text.decode(self.encode_).strip('\0').strip("\n")

