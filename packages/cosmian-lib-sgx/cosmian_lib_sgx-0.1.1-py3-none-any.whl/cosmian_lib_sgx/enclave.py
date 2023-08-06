"""cosmian_lib_sgx.enclave module."""

from contextlib import ContextDecorator
from io import BytesIO
from pathlib import Path
from typing import Iterator, Optional

from cosmian_lib_sgx.args import parse_args
from cosmian_lib_sgx.crypto_lib import is_running_in_enclave
from cosmian_lib_sgx.import_hook import import_set_key
from cosmian_lib_sgx.reader import InputData
from cosmian_lib_sgx.writer import OutputData


class Enclave(ContextDecorator):
    def __init__(self):
        self.keys = parse_args()
        self.root_path = Path.cwd().absolute()
        self.input_data: InputData = InputData(
            root_path=self.root_path,
            keys=self.keys
        )
        self.output_data: OutputData = OutputData(
            root_path=self.root_path,
            keys=self.keys
        )

    def __enter__(self):
        if is_running_in_enclave() is True:
            import_set_key(self.keys)

        return self

    def __exit__(self, *exc):
        return False

    def read(self, n: Optional[int] = None) -> Iterator[BytesIO]:
        return self.input_data.read(n)

    def write(self, data: bytes, n: Optional[int] = None):
        return self.output_data.write(data, n)
