
from nr.util.parsing import Cursor, Scanner


def test_seek():
  s = Scanner("foo\nbar")
  assert s.char == 'f'
  assert s.pos == Cursor(0, 1, 1)

  s.next()
  assert s.char == 'o'
  assert s.pos == Cursor(1, 1, 2)

  s.seek(5)
  assert s.char == 'a'
  assert s.pos == Cursor(5, 2, 2)

  s.seek(-1, 'cur')
  assert s.char == 'b'
  assert s.pos == Cursor(4, 2, 1)

  s.seek(-1, 'cur')
  assert s.char == '\n'
  assert s.pos == Cursor(3, 1, 4)

  s.seek(-1, 'cur')
  assert s.char == 'o'
  assert s.pos == Cursor(2, 1, 3)

  s.seek(-1, 'cur')
  assert s.char == 'o'
  assert s.pos == Cursor(1, 1, 2)

  s.seek(-1, 'cur')
  assert s.char == 'f'
  assert s.pos == Cursor(0, 1, 1)

  # At the start, seek ingored.
  s.seek(-1, 'cur')
  assert s.char == 'f'
  assert s.pos == Cursor(0, 1, 1)

  s.seek(0, 'end')
  assert s.char == ''
  assert s.pos == Cursor(7, 2, 4)

  s.seek(-20, 'cur')
  assert s.char == 'f'
  assert s.pos == Cursor(0, 1, 1)


def test_seek_long_text():
  """ Tests the competence of #Scanner.seek() and ensures that counting of line numbers and column offsets
  works the same whether you seek to the position or crawl to it with #Scanner.next(). """

  text = '\n'.join(['012345678'] * 3)
  s1 = Scanner(text)
  s2 = Scanner(text)

  for lineno in range(3):
    for colno in range(10):
      index = lineno * 10 + colno
      expected_char = '' if index >= len(text) else text[index]
      s1.seek(index)
      assert (s1.char, s1.pos) == (expected_char, Cursor(index, lineno + 1, colno + 1))
      assert (s2.char, s2.pos) == (expected_char, Cursor(index, lineno + 1, colno + 1))
      s2.next()

  assert s1.pos == s2.pos
  assert s2.char == ''


def test_match():
  s = Scanner('foobar')
  assert not s.match('bar')
  assert s.pos.offset == 0

  m = s.match('.oo')
  assert m is not None
  assert m.start() == 0
  assert m.group(0) == 'foo'

  m = s.match('.*')
  assert m is not None
  assert m.start() == 3
  assert s.pos.offset == 6
  assert m.group(0) == 'bar'


def test_search():
  s = Scanner('foobar')
  m = s.search('ba.')
  assert m is not None
  assert m.start() == 3
  assert m.group(0) == 'bar'
  assert s.pos.offset == 6
