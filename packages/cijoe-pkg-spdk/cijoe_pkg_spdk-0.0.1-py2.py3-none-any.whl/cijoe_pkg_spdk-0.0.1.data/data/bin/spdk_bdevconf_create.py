#!/usr/bin/env python3
"""
    Fooo
"""
import argparse
import json
import sys


def parse_args():
    """Parse command-line arguments"""

    # Parse the Command-Line
    prsr = argparse.ArgumentParser(
        description='Emit a SPDK/bdev/xNVMe configuration in json-format',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    prsr.add_argument(
        "--filename",
        help="Bdev filename",
        required=True
    )
    prsr.add_argument(
        '--bs',
        default=512,
        type=int,
        help="Block size in bytes",
    )
    prsr.add_argument(
        '--be',
        default="linux",
        help="Restrict backend to the given argument",
    )
    prsr.add_argument(
        '--be_async',
        help="Asynchronous I/O for bdev to use",
        required=True,
    )

    args = prsr.parse_args()

    return args


def main(args):
    """..."""

    print(json.dumps({
        "subsystems": [{
            "subsystem": "bdev",
            "config": [{
                "method": "bdev_xnvme_create",
                "params": {
                    "name": "bdev_auto",
                    "filename": args.filename,
                    "be": args.be,
                    "sync": args.be_async,
                    "block_size": args.bs
                }
            }]
        }],
    }, indent=4))


if __name__ == "__main__":
    sys.exit(main(parse_args()))
