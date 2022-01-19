
import pytest
from nr.util.keyvalue.sqlite import SqliteDatastore


def test_sqlite_datastore():
  ds = SqliteDatastore(':memory:')
  kv = ds.get_namespace('foobar')

  assert list(ds.get_namespaces()) == ['foobar']

  with pytest.raises(ValueError) as excinfo:
    kv.get('spam')
  assert str(excinfo.value) == "key 'foobar'/'spam' does not exist"

  kv.set('spam', b'hello world')
  assert kv.get('spam') == b'hello world'
  assert list(kv.keys()) == ['spam']
  assert list(kv.keys('spa')) == ['spam']
  assert list(kv.keys('bar')) == []
