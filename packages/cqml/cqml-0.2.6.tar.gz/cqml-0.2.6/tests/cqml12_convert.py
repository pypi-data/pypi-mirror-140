#!/usr/bin/env python3
import pytest, sys
from .context import cqml

if len(sys.argv) > 1:
    files = sys.argv[1:]
    for file in files:
        print(file)
        cqml.upgrade_file(file)
