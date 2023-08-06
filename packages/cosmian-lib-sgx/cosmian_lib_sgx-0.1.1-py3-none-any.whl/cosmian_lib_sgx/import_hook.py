"""cosmian_lib_sgx.import_hook module.

Examples
--------
>>> import sys
>>> from cosmian_lib_sgx import import_hook
>>> key: bytes = bytes.fromhex("0102030405060708090a0102030405060708090a0102030405060708090a0102")
>>> import_hook.import_set_key(key)
>>> # then import your ciphered module

See Also
--------
https://stackoverflow.com/questions/43571737/how-to-implement-an-import-hook-that-can-modify-the-source-code-on-the-fly-using

"""

from importlib.abc import Loader, MetaPathFinder
from importlib.util import spec_from_file_location
import os.path
from pathlib import Path
import sys
from typing import Dict, List

from cosmian_lib_sgx.crypto_lib import enclave_decrypt
from cosmian_lib_sgx.key_info import KeyInfo
from cosmian_lib_sgx.side import Side


class CipheredMetaFinder(MetaPathFinder):
    """CipheredMetaFinder class."""

    def __init__(self, key: bytes) -> None:
        self.key: bytes = key

    def find_spec(self, fullname: str, path: List[str], target=None):
        # print((fullname, path, target))
        if not path:
            cwd = os.getcwd()
            if cwd not in sys.path:
                sys.path.append(os.getcwd())
            path = sys.path

        if "." in fullname:
            *_, name = fullname.split(".")
        else:
            name = fullname

        for entry in path:
            if os.path.isdir(os.path.join(entry, name)):
                # this module has child modules
                _filename = os.path.join(entry, name, "__init__.py.enc")
                filename = os.path.join(entry, name, "__init__.py")
                submodule_locations = [os.path.join(entry, name)]
            else:
                _filename = os.path.join(entry, name + ".py.enc")
                filename = os.path.join(entry, name + ".py")
                submodule_locations = None

            if os.path.exists(_filename):
                # print("found encrypted module: ", _filename)

                # handle this encrypted file with the Cosmian loader
                return spec_from_file_location(
                    fullname,
                    filename,
                    loader=CipheredLoader(
                        _filename,
                        self.key
                    ),
                    submodule_search_locations=submodule_locations
                )
            elif os.path.exists(filename):
                # not us, use the standard loader
                return None
            else:
                # try next path
                continue

        return None  # we don't know how to import this


class CipheredLoader(Loader):
    """CipheredLoader class."""

    def module_repr(self, module):
        raise NotImplementedError

    def __init__(self,
                 filename: str,
                 key: bytes) -> None:
        self.filename: str = filename
        self.key: bytes = key

    def create_module(self, spec):
        return None  # use default module creation semantics

    def exec_module(self, module):
        with open(self.filename, 'rb') as f:
            ciphered_module = f.read()
            plain_module = enclave_decrypt(
                encrypted_data=ciphered_module,
                sealed_key=self.key
            ).decode("utf-8")
            exec(plain_module, vars(module))


def import_set_key(keys: Dict[Side, List[KeyInfo]]) -> None:
    if Side.CodeProvider not in keys:
        raise Exception("Key not found for Code Provider!")

    if len(keys[Side.CodeProvider]) != 1:
        raise Exception("Security issue, multiple Code Provider key found!")

    key_info, *_ = keys[Side.CodeProvider]

    """Inserts the finder into the import machinery."""
    sys.meta_path.insert(0, CipheredMetaFinder(key_info.enc_symkey))


def decrypt_params(path: Path,
                   key: bytes) -> bytes:
    """Used to decrypt input `path`."""
    if not path.is_file():
        raise FileNotFoundError(f"Can't find '{path}'!")

    ciphertext: bytes
    with open(path, 'rb') as f:
        ciphertext = f.read()
    plaintext = enclave_decrypt(
        encrypted_data=ciphertext,
        sealed_key=key,
    )

    return plaintext
