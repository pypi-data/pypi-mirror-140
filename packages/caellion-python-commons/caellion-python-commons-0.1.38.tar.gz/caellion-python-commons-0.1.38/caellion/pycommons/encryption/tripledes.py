"""!
This module provides utilities related to or using 3DES symmetric encryption algorithm
"""

import pyDes
import hashlib
import base64


class TripleDESECBMD5Key:
    """!
    This class provides implementation of triple DES algorithm which uses MD5 hash of password as a key (it uses 16-byte key so it is triple DES with 2 keys)
    """

    password = ""
    encryptionKey = ""
    DES3 = None
    padmode = pyDes.PAD_PKCS5

    def __init__(self, password):
        """!
        Sets up the class for use

        @param password password to use for key generation
        """
        self.password = password.encode("ASCII", errors="replace")
        md5 = hashlib.md5()
        md5.update(self.password)
        hash = md5.digest()
        self.encryptionKey = hash

        self.DES3 = pyDes.triple_des(self.encryptionKey, pyDes.ECB, padmode=self.padmode)

    def encrypt(self, data):
        """!
        Encrypts data with 3DES ECB algorithm

        @param data data to be encrypted

        @returns base64-encoded 3DES encrypted string
        """
        cipher = self.DES3.encrypt(data, padmode=self.padmode)
        return base64.encodebytes(cipher).decode("ASCII").strip()

    def decrypt(self, cipher):
        """!
        Decodes and decrypts Base64-encoded 3DES-encrypted data

        @param cipher base64-encoded encrypted data to decrypt

        @returns decrypted string
        """
        cipher = base64.decodebytes((cipher).encode("ASCII"))
        data = self.DES3.decrypt(cipher, padmode=self.padmode)
        data = data.decode("ASCII")
        return data
