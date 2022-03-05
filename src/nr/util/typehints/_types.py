
""" Stable API to inspect Python #typing type hints. """

from __future__ import annotations
import abc
import enum
import dataclasses
import sys
import typing as t
from ._utils import type_repr


@dataclasses.dataclass
class TypeParameters:
  """ Contains details about the parameters and parametrization of a generic type. """

  parameters: t.Tuple[t.TypeVar, ...]
  values: t.Optional[t.Tuple[BaseType, ...]]


class BaseType(abc.ABC):
  """ Base class for an API representation of #typing type hints. """

  def __init__(self) -> None:
    raise TypeError(f'{type(self).__name__} cannot be constructed')

  @abc.abstractmethod
  def to_typing(self) -> t.Any:
    """ Convert the type hint back to a #typing representation. """

  def visit(self, func: t.Callable[['BaseType'], 'BaseType']) -> 'BaseType':
    """ Visit the type hint and its nested hints with a transforming callback. """
    return func(self)


@dataclasses.dataclass
class _GenericSingleArgType(BaseType):

  type: BaseType

  _type_hint: t.ClassVar[t.Any]

  def __repr__(self) -> str:
    return f'{self.__class__.__name__}({self.type!r})'

  def to_typing(self) -> t.Any:
    return self._type_hint[self.type.to_typing()]

  def visit(self, func: t.Callable[['BaseType'], 'BaseType']) -> 'BaseType':
    return func(self.__class__(self.type.visit(func)))


@dataclasses.dataclass
class _GenericMultipleArgsType(BaseType):

  types: t.Tuple[BaseType, ...]

  _type_hint: t.ClassVar[t.Any]

  def __repr__(self) -> str:
    return f'{self.__class__.__name__}({", ".join(map(repr, self.types))})'

  def to_typing(self) -> t.Any:
    return self._type_hint[tuple(x.to_typing() for x in self.types)]

  def visit(self, func: t.Callable[['BaseType'], 'BaseType']) -> 'BaseType':
    return func(self.__class__(tuple(t.visit(func) for t in self.types)))


@dataclasses.dataclass
class _SpecialFormType(BaseType):
  _type_hint: t.ClassVar[t.Any]

  def __repr__(self) -> str:
    return f'{type(self).__name__}()'

  def to_typing(self) -> t.Any:
    return self._type_hint


@dataclasses.dataclass
class Alias(_GenericSingleArgType):
  """ Represents #typing.NewType. """

  name: str

  def to_typing(self) -> t.Any:
    return t.NewType(self.name, self.type.to_typing())


@dataclasses.dataclass
class Annotated(_GenericSingleArgType):
  """ Represents #typing.Union. Note that #typing.Optional is also represented as this type. """

  _type_hint = t.Annotated

  annotations: t.Tuple[t.Any, ...]

  def to_typing(self) -> t.Any:
    return self._type_hint[(self.type.to_typing(),) + self.annotations]


class Any(_SpecialFormType):
  """ Represents #typing.Any. """

  _type_hint = t.Any


class ClassVar(_GenericSingleArgType):
  """ Represents #typing.ClassVar. """

  _type_hint = t.ClassVar


@dataclasses.dataclass
class Concrete(BaseType):
  """ Represents a concrete Python type.

  If the type is generic (including special generic aliases like #typing.List or #typing.Mapping), the type
  parameters are stored in this representation as well.

  Note that `None` is represented as `Concrete(NoneType)`.
  """

  python_type: t.Type
  parameters: TypeParameters | None = None

  def __repr__(self) -> str:
    return f'{self.__class__.__name__}({type_repr(self.python_type)})'

  def to_typing(self) -> t.Any:
    return self.python_type

  def visit(self, func: t.Callable[['BaseType'], 'BaseType']) -> 'BaseType':
    return func(self.__class__(self.python_type.visit(func)))


class Final(_GenericSingleArgType):
  """ Represents #typing.Final. """

  _type_hint = t.Final


@dataclasses.dataclass
class ForwardRef(BaseType):
  """ Represents a #typing.ForwardRef. """

  code: str
  module: str

  def __post_init__(self) -> None:
    self.__code = compile(self.code, f'<module {self.module!r}>', 'eval')

  def __repr__(self) -> str:
    return f'{self.__class__.__name__}(code={self.code!r}, module={self.module!r})'

  def to_typing(self) -> t.Any:
    return t.ForwardRef(self.code, module=self.module)

  def evaluate(self) -> t.Any:
    module = sys.modules[self.module]
    return eval(self.code, vars(module))


@dataclasses.dataclass
class Literal(BaseType):
  """ Represents #typing.Literal. """

  values: t.Tuple[t.Union[int, bytes, str, bool, enum.Enum, None], ...]

  def __repr__(self) -> str:
    return f'Literal({self.values!r})'

  def to_typing(self) -> t.Any:
    return t.Literal[self.values]


class NoReturn(_SpecialFormType):
  """ Represents #typing.NoReturn. """

  _type_hint = t.NoReturn


class TypeGuard(_GenericSingleArgType):
  """ Represents #typing.TypeGuard. """

  _type_hint = t.TypeGuard


@dataclasses.dataclass
class Unknown(BaseType):
  """ Represents an unknown type hint. """

  value: t.Any

  def __repr__(self) -> str:
    return f'{self.__class__.__name__}({self.value!r})'

  def to_typing(self) -> t.Any:
    return self.value


class Union(_GenericMultipleArgsType):
  """ Represents #typing.Union. Note that #typing.Optional is also represented as this type. """

  _type_hint = t.Union
