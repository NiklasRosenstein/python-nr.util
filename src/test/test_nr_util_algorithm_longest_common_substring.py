
from nr.util.algorithm import longest_common_substring


def test_longest_common_substring():
  assert longest_common_substring('abcdefg', 'gcdefika') == 'cdef'
  assert longest_common_substring('nr.util.parsing', 'nr.util') == 'nr.util'
  assert longest_common_substring('nr.util', 'nr.util.parsing') == 'nr.util'
  assert longest_common_substring('foo', 'bar') == ''
  assert longest_common_substring('foo', 'barometer') == 'o'
