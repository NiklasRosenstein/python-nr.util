
import typing as t

from nr.util.generic import T_contra


class Consumer(t.Protocol[T_contra]):

  def __call__(self, value: T_contra) -> t.Any:
    ...
