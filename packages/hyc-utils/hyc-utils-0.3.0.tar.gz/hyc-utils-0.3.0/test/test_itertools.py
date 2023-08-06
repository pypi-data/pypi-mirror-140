import pytest

import utils

@pytest.mark.parametrize('s, depth, expected', [
    ([[1,2,[3]],[],(4,5),6], 1, [1,2,[3],4,5,6]),
    ([[1,2,[3]],[],(4,5),6], -1, [1,2,3,4,5,6]),
    (tuple([[1,2,[3]],[],(4,5),6]), -1, (1,2,3,4,5,6)),
])
def test_flatten_seq(s, depth, expected):
    assert str(utils.itertools.flatten_seq(s, depth=depth)) == str(expected)
    
@pytest.mark.parametrize('d, depth, expected', [
    ({'a': {'b': {'c': 'd'}}}, 1, {('a','b'): {'c': 'd'}}),
    ({'a': {'b': {'c': 'd'}}}, -1, {('a','b','c'):'d'}),
])
def test_flatten_dict(d, depth, expected):
    assert str(utils.itertools.flatten_dict(d, depth=depth)) == str(expected)
    
@pytest.mark.parametrize('d, keys, value, expected', [
    ({}, ['a', 'b'], 'c', {'a': {'b': 'c'}}),
])
def test_assign_dict(d, keys, value, expected):
    utils.itertools.assign_dict(d, keys, value)
    assert str(d) == str(expected)