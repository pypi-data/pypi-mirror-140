"""cosmian_lib_sgx.key_info module."""

from hashlib import sha3_256
from pathlib import Path


class KeyInfo:
    def __init__(self, pubkey: bytes, enc_symkey: bytes):
        self.pubkey: bytes = pubkey
        self.fingerprint: str = sha3_256(self.pubkey).digest()[-8:].hex()
        self.enc_symkey: bytes = enc_symkey

    @classmethod
    def from_path(cls, path: Path):
        hexa: str
        hexa, *_ = path.stem.split(".")
        pubkey: bytes = bytes.fromhex(hexa)
        enc_symkey: bytes = path.read_bytes()

        return cls(pubkey, enc_symkey)
