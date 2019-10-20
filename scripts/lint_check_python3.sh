#!/usr/bin/env bash
set -eou pipefail

# R = refactor
# C = convention
# W = warning

# adbtool\adbtool.py:20:0: R0903: Too few public methods (0/2) (too-few-public-methods)
# C0111: Missing function docstring (missing-docstring)
python3 -m pylint adbtool tests/*.py setup.py --disable=C,R0123,R0903,R0911,R0912,R0914,R0915,R1705,R1710,C0103,C0111,C0301,C0302,C0411,C0413,C1801,W0511,W0621,W0601,W0603
