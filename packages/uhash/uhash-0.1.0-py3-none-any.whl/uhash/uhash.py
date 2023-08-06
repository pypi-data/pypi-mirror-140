#!/usr/bin/env python
# -*- coding: utf-8 -*-
from hashlib import md5
from base64 import b64encode, b64decode
from Crypto.Cipher import DES3
from Crypto.Util.Padding import unpad
from numpy import pad

from uhash.config import URBOX_SECRET


class UHash(object):
    def __init__(self):
        self.secret = URBOX_SECRET

    def encode(self, data: str, key: str = None) -> str:
        if not key:
            key = self.secret

        md5_key = md5(key.encode("utf-8")).hexdigest()[0:24]
        data_bytes = bytes(data.encode("utf-8"))
        cipher_txt = (b64encode(data_bytes)).decode("utf-8").replace("=", "")
        cipher = DES3.new(md5_key, DES3.MODE_ECB)
        plain_txt = cipher.encrypt(pad(cipher_txt.encode("utf-8"), DES3.block_size))

        try:
            cipher_base64 = b64encode(plain_txt, altchars="-_".encode("utf-8")).decode("utf-8")
        except Exception:
            cipher_base64 = b64encode(plain_txt).decode('utf-8')
            cipher_base64 = cipher_base64.replace('/', '_').replace('+', '-')

        txt = cipher_base64.replace("=", "")
        return txt

    def decode(self, data: str, key: str = None, is_base64: bool = True) -> str:
        if not key:
            key = self.secret

        md5_key = md5(key.encode("utf-8")).hexdigest()[0:24]
        spacing = '=' * (-len(data) % 4)
        data = "{data}{spacing}".format(data=data, spacing=spacing)

        try:
            cipher_txt = b64decode(data, altchars="-_")
        except Exception as e:
            data = data.replace('-', '+').replace('_', '/')
            cipher_txt = b64decode(data)

        cipher = DES3.new(md5_key, DES3.MODE_ECB)
        cipher_decrypt = cipher.decrypt(cipher_txt)
        cipher_unpad = unpad(cipher_decrypt, DES3.block_size)
        cipher_unpad_txt = cipher_unpad.decode("utf-8")
        if is_base64 is True:
            cipher_unpad_txt = "{txt}=".format(txt=cipher_unpad_txt)
            bytes_cipher_unpad_txt = bytes(cipher_unpad_txt.encode("utf-8"))
            txt = b64decode(bytes_cipher_unpad_txt + b'=' * (-len(bytes_cipher_unpad_txt) % 4)).decode("utf-8")
        else:
            txt = cipher_unpad_txt
        return txt


uhash = UHash()
