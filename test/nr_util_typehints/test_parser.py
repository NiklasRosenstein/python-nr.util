
import typing as t
import typing_extensions as te

import pytest
from nr.util import typehints as types
from nr.util.typehints import parse_type_hint


def test_Alias():
  assert parse_type_hint(t.NewType('MyInt', int)) == types.Alias(types.Concrete(int), 'MyInt')


def test_Any():
  assert parse_type_hint(t.Any) == types.Any()


def test_Annotated():
  assert parse_type_hint(te.Annotated[int, 42]) == types.Annotated(types.Concrete(int), (42,))


def test_Concrete():
  assert parse_type_hint(int) == types.Concrete(int)


def test_ClassVar():
  assert parse_type_hint(te.ClassVar[int]) == types.ClassVar(types.Concrete(int))


def test_Final():
  assert parse_type_hint(te.Final[int]) == types.Final(types.Concrete(int))


def test_ForwardRef():
  assert parse_type_hint('str', __name__) == types.ForwardRef('str', __name__)
  with pytest.raises(AssertionError):
    assert parse_type_hint('str')
  assert types.ForwardRef('str', __name__).evaluate() is str
  assert parse_type_hint(list['str'], __name__) == types.Concrete(list, types.TypeParameters((), (types.ForwardRef('str', __name__),)))
  assert parse_type_hint(t.List['str'], __name__) == types.Concrete(list, types.TypeParameters((), (types.ForwardRef('str', __name__),)))



def test_NoReturn():
  assert parse_type_hint(te.NoReturn) == types.NoReturn()


def test_TypeGuard():
  assert parse_type_hint(te.TypeGuard[int]) == types.TypeGuard(types.Concrete(int))


def test_Unknown():
  assert parse_type_hint(42) == types.Unknown(42)


def test_Union():
  assert parse_type_hint(t.Union[int, str]) == types.Union((types.Concrete(int), types.Concrete(str)))
  assert parse_type_hint(t.Union[int, str, None]) == types.Union((types.Concrete(int), types.Concrete(str), types.Concrete(type(None))))
  assert parse_type_hint(t.Optional[int]) == types.Union((types.Concrete(int), types.Concrete(type(None))))


def test_Literal():
  assert parse_type_hint(te.Literal[42, 'spam', None]) == types.Literal((42, 'spam', None))


def test_special_generics():
  import collections.abc
  assert parse_type_hint(list) == types.Concrete(list, types.TypeParameters((), (types.Any(),)))
  assert parse_type_hint(t.List) == types.Concrete(list, types.TypeParameters((), (types.Any(),)))
  assert parse_type_hint(list[int]) == types.Concrete(list, types.TypeParameters((), (types.Concrete(int),)))
  assert parse_type_hint(t.List[int]) == types.Concrete(list, types.TypeParameters((), (types.Concrete(int),)))
  assert parse_type_hint(t.Mapping) == types.Concrete(collections.abc.Mapping, types.TypeParameters((), (types.Any(), types.Any(),)))
  assert parse_type_hint(t.Mapping[str, int]) == types.Concrete(collections.abc.Mapping, types.TypeParameters((), (types.Concrete(str), types.Concrete(int),)))
  assert parse_type_hint(t.MutableMapping[str, int]) == types.Concrete(collections.abc.MutableMapping, types.TypeParameters((), (types.Concrete(str), types.Concrete(int),)))
  assert parse_type_hint(dict) == types.Concrete(dict, types.TypeParameters((), (types.Any(), types.Any(),)))
  assert parse_type_hint(t.Dict) == types.Concrete(dict, types.TypeParameters((), (types.Any(), types.Any(),)))
  assert parse_type_hint(dict[str, int]) == types.Concrete(dict, types.TypeParameters((), (types.Concrete(str), types.Concrete(int),)))
  assert parse_type_hint(t.Dict[str, int]) == types.Concrete(dict, types.TypeParameters((), (types.Concrete(str), types.Concrete(int),)))


def test_special_generic_subclass():
  T = t.TypeVar('T')
  class MyList(t.List[T]):
    pass
  assert parse_type_hint(MyList) == types.Concrete(MyList, types.TypeParameters((T,), None))
  assert parse_type_hint(MyList[int]) == types.Concrete(MyList, types.TypeParameters((T,), (types.Concrete(int),)))

  class MyList2(t.List[int]):
    pass
  assert parse_type_hint(MyList2) == types.Concrete(MyList2, types.TypeParameters((), None))


def test_custom_generic_class():
  T = t.TypeVar('T')
  class MyClass(t.Generic[T]):
    pass
  assert parse_type_hint(MyClass) == types.Concrete(MyClass, types.TypeParameters((T,), None))
  assert parse_type_hint(MyClass[int]) == types.Concrete(MyClass, types.TypeParameters((T,), (types.Concrete(int),)))

  class MySubclass(MyClass[int]):
    pass
  assert parse_type_hint(MySubclass) == types.Concrete(MySubclass, types.TypeParameters((), None))
