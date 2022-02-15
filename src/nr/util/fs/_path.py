
from pathlib import Path


def is_relative_to(a: Path | str, b: Path | str) -> bool:
  """ Returns `True` if path *a* is relative to path *b*. """

  try:
   Path (a).relative_to(b)
  except ValueError:
    return False
  return True
