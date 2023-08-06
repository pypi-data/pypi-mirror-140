"""cosmian_lib_sgx.writer module."""

from pathlib import Path
from typing import List, Dict, Optional

from cosmian_lib_sgx.side import Side
from cosmian_lib_sgx.key_info import KeyInfo
from cosmian_lib_sgx.crypto_lib import enclave_encrypt


class OutputData:
    def __init__(self,
                 root_path: Path,
                 keys: Dict[Side, List[KeyInfo]],
                 debug: bool = False) -> None:
        self.debug: bool = debug
        self.root_path: Path = root_path
        self.output_path: Path = self.root_path / "result"
        if not self.debug:
            assert Side.ResultConsumer in keys, "Need at least 1 RC key"
        self.keys: List[KeyInfo] = [] if self.debug else keys[Side.ResultConsumer]

    def write(self, data: bytes, n: Optional[int] = None):
        if self.debug:
            self.output_path.mkdir(parents=True, exist_ok=True)
            (self.output_path / "result.bin").write_bytes(data)
        else:
            for i, key_info in enumerate(self.keys):
                temp_path: Path = self.output_path / key_info.fingerprint
                temp_path.mkdir(parents=True, exist_ok=True)
                if n is None or n == i:
                    (temp_path / "result.bin.enc").write_bytes(
                        enclave_encrypt(data=data,
                                        sealed_key=key_info.enc_symkey)
                    )
