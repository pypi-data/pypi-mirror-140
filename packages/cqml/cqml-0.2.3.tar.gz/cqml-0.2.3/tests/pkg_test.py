#!/usr/bin/env python3
import pytest
from .context import cqml, TEST_YAML
from .db_mock import spark

def test_pkg():
    dict = cqml.pkg_cqml('cqml_test', spark, 'tests')
    assert 'pkg' in dict
    assert 'html' in dict
    assert 'actions' in dict
