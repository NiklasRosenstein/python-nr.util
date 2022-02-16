
from __future__ import annotations

from nr.util import ChainDict


def test_ChainDict():
  a = {'foo': 42}
  b = {'bar': 'spam'}
  c: dict[str, str] = {}
  d: ChainDict[str, str | int] = ChainDict({}, a, b, c)

  assert str(d) == 'ChainDict({})'.format({'foo': 42, 'bar': 'spam'})
  assert d['foo'] == a['foo']
  assert d['bar'] == b['bar']
  assert sorted(d.keys()) == ['bar', 'foo']

  d['hello'] = 'World'
  assert a == {'foo': 42}
  assert b == {'bar': 'spam'}
  assert c == {}
  assert d == {'foo': 42, 'bar': 'spam', 'hello': 'World'}

  del d['foo']
  assert a == {'foo': 42}
  assert b == {'bar': 'spam'}
  assert c == {}
  assert d == {'bar': 'spam', 'hello': 'World'}

  d['foo'] = 99
  assert a == {'foo': 42}
  assert b == {'bar': 'spam'}
  assert c == {}
  assert d == {'foo': 99, 'bar': 'spam', 'hello': 'World'}

  d.clear()
  assert a == {'foo': 42}
  assert b == {'bar': 'spam'}
  assert c == {}
  assert d == {}
