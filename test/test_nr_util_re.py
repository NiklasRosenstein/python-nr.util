
from nr.util.re import MatchFullError, match_full
import pytest


def test_match_full():
  matches = [x.groups() for x in match_full(r'(\d+)([A-Z]+)', '30D2A53BO')]
  assert matches == [('30', 'D'), ('2', 'A'), ('53', 'BO')]

  matches = [x.group(0) for x in match_full(r'\d{2}', '1234567890')]
  assert matches == ['12', '34', '56', '78', '90']

  with pytest.raises(MatchFullError) as excinfo:
    list(match_full(r'\d{2}', '123456789'))
  assert excinfo.value.string == '123456789'
  assert excinfo.value.endpos == 8
