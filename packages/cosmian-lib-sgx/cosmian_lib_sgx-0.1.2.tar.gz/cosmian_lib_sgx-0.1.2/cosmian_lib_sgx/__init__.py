"""cosmian_lib_sgx module."""

from .args import parse_args
from .crypto_lib import enclave_encrypt, enclave_decrypt, enclave_x25519_keypair
from .enclave import Enclave
from .import_hook import import_set_key
from .key_info import KeyInfo
from .reader import InputData
from .side import Side
from .writer import OutputData


__all__ = [
    "enclave_encrypt", "enclave_decrypt", "enclave_x25519_keypair",
    "parse_args", "import_set_key",
    "KeyInfo", "InputData", "OutputData", "Side", "Enclave"
]
