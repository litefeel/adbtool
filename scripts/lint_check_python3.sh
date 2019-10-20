#!/usr/bin/env bash
set -eou pipefail

# R = refactor
# C = convention
# W = warning

# adbtool\adbtool.py:20:0: R0903: Too few public methods (0/2) (too-few-public-methods)
# adbtool\adbtool.py:61:8: R1722: Consider using sys.exit() (consider-using-sys-exit)
# C0111: Missing function docstring (missing-docstring)
python3 -m pylint adbtool tests setup.py --disable=C,W,R1722,R0903
