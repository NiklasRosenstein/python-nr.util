
import typing as t
from nr.util.generic import T

_Message = str | t.Callable[[], str]


def _get_message(message: _Message) -> str:
  if isinstance(message, str):
    return message
  else:
    return message()


def assure(v: T | None, msg: _Message | None = None) -> T:
  """ Assures that *v* is not `None` and returns it. If the value is in fact `None`, a {@link ValueError} will
  be raised raised. """

  if v is None:
    raise ValueError(_get_message(msg) if msg else 'expected value to not be None')
  return v
