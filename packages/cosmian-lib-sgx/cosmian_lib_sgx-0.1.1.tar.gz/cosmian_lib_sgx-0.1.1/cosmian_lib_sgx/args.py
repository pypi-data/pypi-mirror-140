"""cosmian_lib_sgx.args module."""

import argparse
import json
import os
from pathlib import Path
import sys
from typing import Dict, List

from cosmian_lib_sgx.crypto_lib import enclave_x25519_keypair, enclave_get_quote
from cosmian_lib_sgx.key_info import KeyInfo
from cosmian_lib_sgx.side import Side


def parse_args() -> Dict[Side, List[KeyInfo]]:
    if int(os.environ.get("RUN", 1)) == 0:  # env RUN=0
        enclave_pubkey, _ = enclave_x25519_keypair()
        # print enclave's public key
        print(enclave_pubkey.hex())
        # dump enclave's quote
        print(json.dumps({
            "isvEnclaveQuote": enclave_get_quote(enclave_pubkey)
        }))
        # exit
        sys.exit(0)

    # env RUN=1
    parser = argparse.ArgumentParser(description="Client keys for code execution")
    main_group = parser.add_argument_group("Main group")
    debug_group = parser.add_argument_group("Debug group")
    main_group.add_argument("--code_provider",
                            help="Code Provider shared key")
    main_group.add_argument("--result_consumers",
                            help="Result Consumer shared keys",
                            nargs="+")
    main_group.add_argument("--data_providers",
                            help="Data Provider shared keys",
                            nargs="+")
    debug_group.add_argument("--debug",
                             help="Debug mode",
                             action="store_true")

    args = parser.parse_args()

    if args.debug:
        return {}

    return {
        Side.CodeProvider: ([KeyInfo.from_path(Path(args.code_provider))]
                            if args.code_provider else []),
        Side.DataProvider: [
            KeyInfo.from_path(Path(shared_key_path))
            for shared_key_path in args.data_providers
        ],
        Side.ResultConsumer: [
            KeyInfo.from_path(Path(shared_key_path))
            for shared_key_path in args.result_consumers
        ]
    }
