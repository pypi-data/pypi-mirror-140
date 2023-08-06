#!/usr/bin/env python3
import pytest
from .context import cqml, TEST_YAML
from .db_mock import spark

@pytest.fixture
def cvm():
    cvm = cqml.make_frames(TEST_YAML, spark, True)
    return cvm

def test_load(cvm):
    assert cvm.df["items"]

def test_select(cvm):
    it = cvm.df["items"]
    assert it
    assert it.item_id
    assert 'item_id' in it.columns
    assert 'sku' in it.columns # alias
    # how to test filter with Mock?

def test_merge(cvm):
    dev = cvm.df["na_devices"]
    assert dev
    assert 'sku' in dev.columns # alias
    assert 'item_id' not in dev.columns # alias

def test_call(cvm):
    n = 11
    a = cvm.cactions[n]
    print(a)
    assert a['id'] == 'days_unseen'
    assert a['sql'] == 'datediff(current_date(),_fivetran_synced)'
