"""cosmian_lib_sgx.enclave module."""

from contextlib import ContextDecorator
from io import BytesIO
from pathlib import Path
from typing import Iterator, Optional, Dict, List

from cosmian_lib_sgx.args import parse_args
from cosmian_lib_sgx.crypto_lib import is_running_in_enclave
from cosmian_lib_sgx.import_hook import import_set_key
from cosmian_lib_sgx.key_info import KeyInfo
from cosmian_lib_sgx.reader import InputData
from cosmian_lib_sgx.side import Side
from cosmian_lib_sgx.writer import OutputData


class Enclave(ContextDecorator):
    def __init__(self, debug: bool = False):
        self.debug: bool = debug
        self.keys: Dict[Side, List[KeyInfo]] = {} if self.debug else parse_args()
        self.root_path: Path = Path.cwd().absolute()
        self.input_data: InputData = InputData(
            root_path=self.root_path,
            keys=self.keys,
            debug=self.debug
        )
        self.output_data: OutputData = OutputData(
            root_path=self.root_path,
            keys=self.keys,
            debug=self.debug
        )

    def __enter__(self):
        if not self.debug and is_running_in_enclave():
            import_set_key(self.keys)

        return self

    def __exit__(self, *exc):
        return False

    def read(self, n: Optional[int] = None) -> Iterator[BytesIO]:
        return self.input_data.read(n)

    def write(self, data: bytes, n: Optional[int] = None):
        return self.output_data.write(data, n)
