
from nr.util.algorithm import longest_common_substring


def test_longest_common_substring():
  assert longest_common_substring('abcdefg', 'gcdefika') == 'cdef'
  assert longest_common_substring('abcdefg', 'gcdefika', start_only=True) == ''
  assert longest_common_substring('nr.util.parsing', 'nr.util') == 'nr.util'
  assert longest_common_substring('nr.util', 'nr.util.parsing') == 'nr.util'
  assert longest_common_substring('nr.util', 'nr.util.parsing', start_only=True) == 'nr.util'
  assert longest_common_substring('foo', 'bar') == ''
  assert longest_common_substring('foo', 'barometer') == 'o'

  assert longest_common_substring(['a', 'b'], ['a', 'b', 'c']) == ['a', 'b']
  assert longest_common_substring(['a', 'b'], ['a', 'b', 'c'], ['f', 'b', 'c']) == ['b']
  assert longest_common_substring(['a', 'b'], ['a', 'b', 'c'], ['f', 'b', 'c'], start_only=True) == []
