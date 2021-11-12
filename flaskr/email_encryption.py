"""
    Use symmetric encryption to store user emails in the databse.
"""
import os
import base64
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet

KEY_FILE=os.path.join(os.path.dirname(__file__), 'secret.key')
SALT=b'ORSO_'

class SymmetricEncryption:
    key: bytes
    fernet: Fernet

    def __init__(self):
        self.key=self.get_key()
        self.fernet=Fernet(self.key)

    def get_key(self):
        p = open(KEY_FILE, 'rb').read()
        kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=SALT,
                iterations=100000,
                backend=default_backend()
                )
        key = base64.urlsafe_b64encode(kdf.derive(p))
        return key

    def enrypt(self, value: str):
        return self.fernet.encrypt(value.encode()).decode()

    def decrypt(self, value: str):
        return self.fernet.decrypt(value.encode()).decode()

encryptor=SymmetricEncryption()
