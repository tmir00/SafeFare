# transitproject/utils.py
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import base64

# AES key must be either 16, 24, or 32 bytes long
AES_KEY = get_random_bytes(32)


def encrypt_data_aes(data):
    """
    Encrypts data using AES-256.
    """
    if data is None:
        return None
    # Convert data to bytes if it's not, as AES requires bytes
    if not isinstance(data, bytes):
        data = data.encode()

    # Create a new cipher object for each encryption
    cipher = AES.new(AES_KEY, AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(data, AES.block_size))

    # Save iv (initialization vector) with ciphertext
    # iv is needed for decryption and it's safe to store it with ciphertext
    iv = base64.b64encode(cipher.iv).decode('utf-8')
    ct = base64.b64encode(ct_bytes).decode('utf-8')

    # The encrypted data will include both the iv and ciphertext
    encrypted_data = f"{iv}:{ct}"
    return encrypted_data


def decrypt_data_aes(encrypted_data):
    """
    Decrypts data encrypted using AES-256.
    """
    if encrypted_data is None:
        return None

    # Split the encrypted data into iv and ciphertext
    iv_str, ct_str = encrypted_data.split(":")
    iv = base64.b64decode(iv_str)
    ct = base64.b64decode(ct_str)

    # Create a new cipher object for decryption
    cipher = AES.new(AES_KEY, AES.MODE_CBC, iv)
    pt = unpad(cipher.decrypt(ct), AES.block_size)
    return pt.decode()

