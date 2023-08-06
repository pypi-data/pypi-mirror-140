"""cosmian_lib_sgx.crypto_lib module."""

from ctypes import *
from pathlib import Path
from typing import Tuple

sgx_crypto_lib_path = Path("/usr/local/lib/libcs_sgx_crypto.so")

if not sgx_crypto_lib_path.exists():
    raise FileNotFoundError(f"Can't find '{sgx_crypto_lib_path}'")

crypto_lib = cdll.LoadLibrary(str(sgx_crypto_lib_path))

# int cs_sgx__init()
crypto_lib.cs_sgx__init.argtypes = []
crypto_lib.cs_sgx__init.restype = c_int

# int cs_sgx__running_inside_enclave()
crypto_lib.cs_sgx__running_inside_enclave.argtypes = []
crypto_lib.cs_sgx__running_inside_enclave.restype = c_int

# int cs_sgx__enclave_x25519_key_pair(unsigned char *pk,
#                                     unsigned char *sk);
crypto_lib.cs_sgx__enclave_x25519_key_pair.argtypes = [
    POINTER(c_ubyte), POINTER(c_ubyte)]
crypto_lib.cs_sgx__enclave_x25519_key_pair.restype = c_int

# int cs_sgx__encrypt_with_sealed_key(unsigned char *encrypted_data,
#                                     const unsigned char *data,
#                                     unsigned long long data_len,
#                                     unsigned char sealed_symkey[static 80]);
crypto_lib.cs_sgx__encrypt_with_sealed_key.argtypes = [
    POINTER(c_ubyte), POINTER(c_ubyte), c_ulonglong, POINTER(c_ubyte)
]
crypto_lib.cs_sgx__encrypt_with_sealed_key.restype = c_int

# int cs_sgx__decrypt_with_sealed_key(unsigned char *data,
#                                     const unsigned char *encrypted_data,
#                                     unsigned long long encrypted_data_len,
#                                     unsigned char sealed_symkey[static 80]);
crypto_lib.cs_sgx__decrypt_with_sealed_key.argtypes = [
    POINTER(c_ubyte), POINTER(c_ubyte), c_ulonglong, POINTER(c_ubyte)
]
crypto_lib.cs_sgx__decrypt_with_sealed_key.restype = c_int

# int cs_sgx__unseal_symkey(unsigned char *symkey,
#                           const unsigned char *encrypted_data,
#                           unsigned long long encrypted_data_len);
crypto_lib.cs_sgx__unseal_symkey.argtypes = [
    POINTER(c_ubyte), POINTER(c_ubyte), c_ulonglong
]
crypto_lib.cs_sgx__unseal_symkey.restype = c_int

# int cs_sgx__get_quote(const unsigned char* user_report_data_str,
#                       char* b64_quote);
crypto_lib.cs_sgx__get_quote.argtypes = [
    POINTER(c_ubyte), c_char_p
]
crypto_lib.cs_sgx__get_quote.restype = c_int

if crypto_lib.cs_sgx__init() != 0:
    raise Exception("Failed to init libsodium!")


def is_running_in_enclave() -> bool:
    if crypto_lib.cs_sgx__running_inside_enclave() == 0:
        return True

    raise Exception("You're code is not running inside SGX enclave!")


def enclave_x25519_keypair() -> Tuple[bytes, bytes]:
    if is_running_in_enclave():
        pk = (c_ubyte * 32)()
        sk = (c_ubyte * 32)()

        if crypto_lib.cs_sgx__enclave_x25519_key_pair(
                cast(pk, POINTER(c_ubyte)),
                cast(sk, POINTER(c_ubyte))
        ) != 0:
            raise Exception("Failed to get X25519 enclave's keypair!")

        return bytes(pk), bytes(sk)


def enclave_encrypt(data: bytes, sealed_key: bytes) -> bytes:
    if is_running_in_enclave():
        data_len = len(data)
        data_c_array = (c_ubyte * data_len)(*data)

        sealed_key_len = len(sealed_key)
        sealed_key_c_array = (c_ubyte * sealed_key_len)(*sealed_key)

        # crypto_box_NONCEBYTES (24) + crypto_box_MACBYTES (16) = 40
        encrypted_data = (c_ubyte * (data_len + 40))()

        if crypto_lib.cs_sgx__encrypt_with_sealed_key(
                cast(encrypted_data, POINTER(c_ubyte)),
                data_c_array,
                data_len,
                sealed_key_c_array
        ) != 0:
            raise Exception("Failed to encrypt data!")

        return bytes(encrypted_data)


def enclave_decrypt(encrypted_data: bytes, sealed_key: bytes) -> bytes:
    if is_running_in_enclave():
        encrypted_data_len = len(encrypted_data)
        encrypted_data_c_array = (c_ubyte * encrypted_data_len)(*encrypted_data)

        sealed_key_len = len(sealed_key)
        sealed_key_c_array = (c_ubyte * sealed_key_len)(*sealed_key)

        # crypto_box_NONCEBYTES (24) + crypto_box_MACBYTES (16) = 40
        data = (c_ubyte * (encrypted_data_len - 40))()

        if crypto_lib.cs_sgx__decrypt_with_sealed_key(
                cast(data, POINTER(c_ubyte)),
                encrypted_data_c_array,
                encrypted_data_len,
                sealed_key_c_array
        ) != 0:
            raise Exception("Failed to decrypt data!")

        return bytes(data)


def enclave_unseal(encrypted_symkey: bytes) -> bytes:
    if is_running_in_enclave():
        enc_symkey_len = len(encrypted_symkey)
        enc_symkey_c_array = (c_ubyte * enc_symkey_len)(*encrypted_symkey)
        # crypto_box_SEALBYTES (48) = crypto_box_PUBLICKEYBYTES (32) +
        #                             crypto_box_MACBYTES (16)
        symkey = (c_ubyte * (enc_symkey_len - 48))()

        if crypto_lib.cs_sgx__unseal_symkey(
                cast(symkey, POINTER(c_ubyte)),
                enc_symkey_c_array,
                enc_symkey_len
        ) != 0:
            raise Exception("Failed to unseal the symmetric key!")

        return bytes(symkey)


def enclave_get_quote(sgx_report_data: bytes) -> str:
    if is_running_in_enclave():
        if len(sgx_report_data) > 64:
            raise Exception("sgx_report_data_t can't exceed 64 bytes!")

        quote = (c_char * 8192)()
        public_key_c_array = (c_ubyte * len(sgx_report_data))(*sgx_report_data)

        if crypto_lib.cs_sgx__get_quote(public_key_c_array, cast(quote, c_char_p)) != 0:
            raise Exception("Failed to retrieve enclave's quote!")

        return bytes(quote).decode("utf-8").rstrip("\0")
