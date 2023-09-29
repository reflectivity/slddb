"""
    Use symmetric encryption to store user emails in the databse.
"""
import os
import base64
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet

KEY_FILE='secret.key'
SALT=b'ORSO_'

class SymmetricEncryption:
    key: bytes
    fernet: Fernet

    def __init__(self):
        self.key=None
        self.fernet=None

    def get_key(self):
        from . import app

        p = app.open_instance_resource(KEY_FILE, 'rb').read()
        kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=SALT,
                iterations=100000,
                backend=default_backend()
                )
        key = base64.urlsafe_b64encode(kdf.derive(p))
        self.key=key
        self.fernet = Fernet(self.key)

    def enrypt(self, value: str):
        if self.key is None:
            self.get_key()
        return self.fernet.encrypt(value.encode()).decode()

    def decrypt(self, value: str):
        if self.key is None:
            self.get_key()
        try:
            return self.fernet.decrypt(value.encode()).decode()
        except Exception as e:
            return f'ERROR: {repr(e)}'

encryptor=SymmetricEncryption()
