
import typing as t
import typing_extensions as te

from nr.util.generic import T_co


class Supplier(te.Protocol[T_co]):

  def __call__(self) -> T_co:
    ...


class ContextSupplier(Supplier[t.ContextManager[T_co]]):
  ...
