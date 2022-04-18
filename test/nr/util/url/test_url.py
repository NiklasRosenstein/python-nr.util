
import pytest

from nr.util.url import Url


def test__Url__of__can_parses_urls_correctly():
  assert Url.of('abc') == Url(path='abc')
  assert Url.of('abc/foo/bar') == Url(path='abc/foo/bar')
  assert Url.of('http://abc/foo/bar') == Url(scheme='http', hostname='abc', path='/foo/bar')
  assert Url.of('http://:@abc/foo/bar') == Url(scheme='http', hostname='abc', path='/foo/bar', username='', password='')
  assert Url.of('http://user:password@abc/foo/bar') == Url(scheme='http', hostname='abc', path='/foo/bar', username='user', password='password')
  assert Url.of('http://@example.org') == Url(scheme='http', hostname='example.org', username='')


def test__Url__of__raises_errors_on_bad_url():
  with pytest.raises(ValueError):
    Url.of('http://example.org:24foo')


def test__Url__str__produces_correct_urls():
  assert str(Url('http', 'example.org', 'foo/bar', username='user', password='123')) == 'http://user:123@example.org/foo/bar'


def test__Url__str__escapes_special_characters():
  assert str(Url('http', 'example.org', port=8411, username='user name')) == 'http://user%20name:@example.org:8411'


def test__Url__netloc__and_other_properties():
  url = Url.of('https://user:password@host:1337/bar')
  assert url == Url('https', 'host', '/bar', username='user', password='password', port=1337)
  assert url.netloc == 'user:password@host:1337'
  assert url.auth == 'user:password'
  assert url.netloc_no_auth == 'host:1337'

  url = Url.of('https://host/bar')
  assert url == Url('https', 'host', '/bar')
  assert url.netloc == 'host'
  assert url.auth is None
  assert url.netloc_no_auth == 'host'
