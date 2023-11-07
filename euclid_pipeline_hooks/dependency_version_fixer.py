#!/usr/bin/env python3

# Copyright (C) 2012-2023, UNIGE and contributors (for the Euclid Science Ground Segment)
# This file is part of Elements <https://gitlab.euclid-sgs.uk/ST-TOOLS/Elements>
# SPDX-License-Identifier: LGPL-3.0-or-later

""" Script to fix the version of a Elements-base pipeline project dependencies
    It is meant to be run in the pre-commit hook framework
"""

from __future__ import annotations

from typing import Sequence
import argparse
import sys


def _fix_file(filename: str) -> bool:
    return True


def main(argv: Sequence[str] | None=None) -> int:

    parser = argparse.ArgumentParser()
    parser.add_argument('filenames', nargs='*', help='Filenames to fix')
    args = parser.parse_args(argv)

    return_code = 0
    for filename in args.filenames:
        if _fix_file(filename):
            print(f'Fixing {filename}')
            return_code = 1

    return return_code


if __name__ == '__main__':
    raise SystemExit(main())
