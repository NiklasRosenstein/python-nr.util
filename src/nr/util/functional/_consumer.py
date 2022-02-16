
import typing as t
import typing_extensions as te

from nr.util.generic import T_contra


class Consumer(te.Protocol[T_contra]):

  def __call__(self, value: T_contra) -> t.Any:
    ...
