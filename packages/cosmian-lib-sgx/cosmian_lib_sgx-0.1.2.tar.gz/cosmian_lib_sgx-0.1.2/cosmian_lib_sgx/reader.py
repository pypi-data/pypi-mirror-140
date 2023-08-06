"""cosmian_lib_sgx.reader module."""

from io import BytesIO
from pathlib import Path
import re
from typing import Dict, List, Tuple, Optional, Iterator

from cosmian_lib_sgx.side import Side
from cosmian_lib_sgx.key_info import KeyInfo
from cosmian_lib_sgx.crypto_lib import enclave_decrypt

FINGERPRINT_RE = re.compile(r"""(?P<fingerprint>[0-9a-zA-Z]{16})""")


class InputData:
    def __init__(self,
                 root_path: Path,
                 keys: Dict[Side, List[KeyInfo]],
                 debug: bool = False) -> None:
        self.debug: bool = debug
        self.root_path: Path = root_path
        self.input_path: Path = self.root_path / "data"
        if not self.debug:
            assert Side.DataProvider in keys, "Need at least 1 DP key"
        self.keys: List[KeyInfo] = [] if self.debug else keys[Side.DataProvider]

    @staticmethod
    def fingerprint_from_path(path: Path) -> Optional[str]:
        for part in path.parts:
            if m := FINGERPRINT_RE.match(part):
                return m.group()
        return None

    @staticmethod
    def find_fingerprint(
            fingerprint: str,
            keys: List[KeyInfo]
    ) -> Optional[Tuple[int, KeyInfo]]:
        for i, key_info in enumerate(keys):
            if key_info.fingerprint == fingerprint:
                return i, key_info
        return None

    def read(self, n: Optional[int] = None) -> Iterator[BytesIO]:
        if self.debug:
            for path in self.input_path.rglob("*"):
                if path.is_file():
                    yield BytesIO(path.read_bytes())
        else:
            for path in self.input_path.rglob("*.enc"):
                if path.is_file():
                    fingerprint: Optional[str] = InputData.fingerprint_from_path(path)
                    if fingerprint is not None:
                        if res := InputData.find_fingerprint(fingerprint, self.keys):
                            pos: int
                            key_info: KeyInfo
                            pos, key_info = res
                            if n is None or n == pos:
                                yield BytesIO(
                                    enclave_decrypt(encrypted_data=path.read_bytes(),
                                                    sealed_key=key_info.enc_symkey)
                                )
