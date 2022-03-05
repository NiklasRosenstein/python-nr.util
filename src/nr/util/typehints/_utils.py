
import typing as t


def type_repr(typ: t.Any) -> str:
  return t._type_repr(typ)  # type: ignore
