
from nr.util.parsing import Scanner, rules


def test_string_literal():
  assert rules.string_literal().get_token(Scanner(' f"foobar"')) == None
  assert rules.string_literal().get_token(Scanner('f"foobar"')) == 'f"foobar"'
