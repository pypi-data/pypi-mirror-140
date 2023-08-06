#!/usr/bin/env python3
import pytest
from .context import cqml, TEST_YAML

def test_from_file():
        cvm = cqml.from_file(TEST_YAML, None)
        assert(cvm)
        assert(cvm.yaml)
