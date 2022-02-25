
import typing as t
import typing_extensions as te

T_Comparable = t.TypeVar('T_Comparable', bound='Comparable')


class Comparable(te.Protocol):
  def __lt__(self, other: t.Any) -> bool: ...
