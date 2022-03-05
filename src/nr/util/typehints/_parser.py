
from __future__ import annotations
from distutils.spawn import spawn

import dataclasses
import sys
import types
import typing as t
import typing_extensions as te
import warnings

from . import _types
from ._utils import type_repr


from collections.abc import Mapping as _Mapping, MutableMapping as _MutableMapping
_ORIGIN_CONVERSION = {  # TODO: Build automatically
  list: t.List,
  set: t.Set,
  dict: t.Dict,
  _Mapping: t.Mapping,
  _MutableMapping: t.MutableMapping,
}


def unpack_type_hint(hint: t.Any) -> t.Tuple[t.Optional[t.Any], t.List[t.Any]]:
  """
  Unpacks a type hint into it's origin type and parameters. Returns #None if the
  *hint* does not represent a type or type hint in any way.
  """

  if hasattr(te, '_AnnotatedAlias') and isinstance(hint, te._AnnotatedAlias):  # type: ignore
    return te.Annotated, list((hint.__origin__,) + hint.__metadata__)  # type: ignore

  if ((hasattr(t, '_SpecialGenericAlias') and isinstance(hint, t._SpecialGenericAlias))  # type: ignore
      or (isinstance(hint, t._GenericAlias) and getattr(hint, '_special', False))):  # type: ignore
    return hint.__origin__, []

  if isinstance(hint, t._GenericAlias) or (sys.version_info >= (3, 9) and isinstance(hint, t.GenericAlias)):  # type: ignore
    return hint.__origin__, list(hint.__args__)

  if isinstance(hint, type):
    return hint, []

  if isinstance(hint, t._SpecialForm  ):
    return hint, []

  if hasattr(types, 'UnionType') and isinstance(hint, types.UnionType):  # type: ignore
    return t.Union, list(hint.__args__)

  return None, []


def find_generic_bases(type_hint: t.Type, generic_type: t.Optional[t.Any] = None) -> t.List[t.Any]:
  """
  This method finds all generic bases of a given type or generic aliases.

  As a reminder, a generic alias is any subclass of #t.Generic that is indexed with type arguments
  or a special alias like #t.List, #t.Set, etc. The type arguments of that alias are propagated
  into the returned generic bases (except if the base is a #t.Generic because that can only accept
  type variables as arguments).

  Examples:

  ```py
  class MyList(t.List[int]):
    ...
  class MyGenericList(t.List[T]):
    ...
  assert find_generic_bases(MyList) == [t.List[int]]
  assert find_generic_bases(MyGenericList) == [t.List[T]]
  assert find_generic_bases(MyGenericList[int]) == [t.List[int]]
  ```
  """

  type_, args = unpack_type_hint(type_hint)
  params = getattr(type_, '__parameters__', [])
  bases = getattr(type_, '__orig_bases__', [])

  generic_choices: t.Tuple[t.Any, ...] = (generic_type,) if generic_type else ()
  if generic_type and generic_type.__origin__:
    generic_choices += (generic_type.__origin__,)

  result: t.List[t.Any] = []
  for base in bases:
    origin = getattr(base, '__origin__', None)
    if (not generic_type and origin) or \
       (base == generic_type or origin in generic_choices):
      result.append(base)

  for base in bases:
    result += find_generic_bases(base, generic_type)

  # Replace type parameters.
  for idx, hint in enumerate(result):
    origin = _ORIGIN_CONVERSION.get(hint.__origin__, hint.__origin__)
    if origin == t.Generic:  # type: ignore
      continue
    result[idx] = populate_type_parameters(origin, hint.__args__, params, args)

  return result


def populate_type_parameters(
  generic_type: t.Any,
  generic_args: t.List[t.Any],
  parameters: t.List[t.Any],
  arguments: t.List[t.Any]) -> t.Any:
  """
  Given a generic type and it's aliases (for example from `__parameters__`), this function will return an
  alias for the generic type where occurrences of type variables from *parameters* are replaced with actual
  type arguments from *arguments*.

  Example:

  ```py
  assert populate_type_parameters(t.List, [T], [T], [int]) == t.List[int]
  assert populate_type_parameters(t.Mapping, [K, V], [V], [str]) == t.Mapping[K, str]
  ```
  """

  new_args = []
  for type_arg in generic_args:
    arg_index = parameters.index(type_arg) if type_arg in parameters else -1
    if arg_index >= 0 and arg_index < len(arguments):
      new_args.append(arguments[arg_index])
    else:
      new_args.append(type_arg)
  return generic_type[tuple(new_args)]


def get_type_hints(type_: t.Any) -> t.Dict[str, t.Any]:
  """
  Like #typing.get_type_hints(), but always includes extras. This is important when we want to inspect
  #typing_extensions.Annotated hints (without extras the annotations are removed).
  """

  if sys.version_info >= (3, 9):
    return t.get_type_hints(type_, include_extras=True)
  else:
    return t.get_type_hints(type_)



import abc


def is_generic_alias(type_hint: t.Any) -> bool:
  return isinstance(type_hint, t.GenericAlias) or (  # type: ignore[attr-defined]
    hasattr(types, 'GenericAlias') and isinstance(type_hint, types.GenericAlias))


def is_special_generic_alias(type_hint: t.Any) -> bool:
  return isinstance(type_hint, t._SpecialGenericAlias)  # type: ignore[attr-defined]


class TypeParserPlugin(abc.ABC):

  @abc.abstractmethod
  def parse_type(self, context: TypeContext) -> t.Optional[_types.BaseType]: ...

  @staticmethod
  def all() -> t.List[TypeParserPlugin]:
    return [cls() for cls in TypeParserPlugin.__subclasses__()]  # type: ignore


class ConcreteTypeParser(TypeParserPlugin):

  def parse_type(self, context: TypeContext) -> t.Optional[_types.BaseType]:
    if not isinstance(context.type_hint, type) or is_generic_alias(context.type_hint) or context.type_hint in _ORIGIN_CONVERSION:
      return None

    # Handle subclasses of special formsm like "class MyList(t.List[T]):"
    if issubclass(context.type_hint, t.Generic):  # type: ignore[arg-type]
      # Without parametrization, like "MyList"
      if context.generic == context.type_hint:
        assert not context.args
        return _types.Concrete(
          context.generic,
          _types.TypeParameters(context.type_hint.__parameters__, None)  # type: ignore[attr-defined]
        )
      # With parametrization, like "MyList[int]"
      else:
        assert context.args
        assert isinstance(context.generic, type)
        return _types.Concrete(
          context.generic,
          _types.TypeParameters(
            context.generic.__parameters__,  # type: ignore[attr-defined]
            tuple(context.push(x).parse_type() for x in context.args)
          )
        )

    else:
      return _types.Concrete(context.type_hint, None)


class SpecialFormParser(TypeParserPlugin):

  def parse_type(self, context: TypeContext) -> t.Optional[_types.BaseType]:
    if context.type_hint == t.Any:
      return _types.Any()
    elif context.generic == te.Annotated:
      assert len(context.args) >= 1
      return _types.Annotated(context.push(context.args[0]).parse_type(), tuple(context.args[1:]))
    elif context.generic == te.ClassVar:
      assert len(context.args) == 1
      return _types.ClassVar(context.push(context.args[0]).parse_type())
    elif context.generic == te.Final:
      assert len(context.args) == 1
      return _types.Final(context.push(context.args[0]).parse_type())
    elif context.generic == te.NoReturn:
      return _types.NoReturn()
    elif context.generic == te.TypeGuard:
      assert len(context.args) == 1
      return _types.TypeGuard(context.push(context.args[0]).parse_type())
    elif context.generic == t.Union:
      return _types.Union(tuple(context.push(x).parse_type() for x in context.args))
    elif context.generic == t.Literal:
      return _types.Literal(tuple(context.args))
    elif isinstance(context.type_hint, t.NewType):  # type: ignore[arg-type]
      return _types.Alias(context.push(context.type_hint.__supertype__).parse_type(), context.type_hint.__name__)
    elif isinstance(context.type_hint, str):
      assert context.module is not None, 'encountered str as ForwardRef but no module reference in TypeContext'
      return _types.ForwardRef(context.type_hint, context.module)
    elif isinstance(context.type_hint, t.ForwardRef):
      module = context.type_hint.__forward_module__ or context.module  # type: ignore[attr-defined]
      assert module is not None, 'encountered a ForwardRef but no module reference in TypeContext'
      return _types.ForwardRef(context.type_hint.__forward_arg__, module)
    return None


class GenericAliasParser(TypeParserPlugin):

  def parse_type(self, context: TypeContext) -> t.Optional[_types.BaseType]:
    if is_generic_alias(context.type_hint):
      assert context.generic != context.type_hint
      assert context.args
      # Handle "list[int]" or "dict[str, str]", also generic aliases of "t.Generic" subclasses.
      # "list" or "dict" don't have __parameters__, but "t._GenericAlias" does
      parameters = getattr(context.generic, '__parameters__', ())
      assert isinstance(context.generic, type)
      return _types.Concrete(
        context.generic,
        _types.TypeParameters(
          parameters,
          tuple(context.push(x).parse_type() for x in context.args)
        )
      )

    # Convert "list" to "typing.List"
    generic = _ORIGIN_CONVERSION.get(context.generic, context.generic)  # type: ignore[arg-type]

    # Handle "t.List", etc. without parameters (all parameters are treated as t.Any).
    if is_special_generic_alias(context.generic):
      return _types.Concrete(
        generic.__origin__,  # type: ignore[union-attr]
        _types.TypeParameters(
          (),
          (_types.Any(),) * generic._nparams  # type: ignore[union-attr]
        )
      )

    return None


@dataclasses.dataclass
class TypeContext:
  parser: TypeParser
  type_hint: t.Any
  module: str | None

  def __post_init__(self) -> None:
    self.generic, self.args = unpack_type_hint(self.type_hint)

  def push(self, type_hint: t.Any, module: str | None = None) -> TypeContext:
    return TypeContext(self.parser, type_hint, module or self.module)

  def parse_type(self) -> _types.BaseType:
    return self.parser.parse_type(self.type_hint, self.module)


@dataclasses.dataclass
class TypeParser:
  plugins: t.List[TypeParserPlugin] = dataclasses.field(default_factory=TypeParserPlugin.all)

  def parse_type(self, type_hint: t.Any, module: str | None = None) -> _types.BaseType:
    context = TypeContext(self, type_hint, module)
    for parser in self.plugins:
      result = parser.parse_type(context)
      if result is not None:
        return result
    return _types.Unknown(type_hint)


def parse_type_hint(type_hint: t.Any, module: str | None = None) -> _types.BaseType:
  return TypeParser().parse_type(type_hint, module)


def evaluate_forward_refs(type_: _types.BaseType) -> _types.BaseType:
  def _visitor(type_: _types.BaseType) -> _types.BaseType:
    if isinstance(type_, _types.ForwardRef):
      return parse_type_hint(type_.evaluate(), type_.module)
    return type_
  return type_.visit(_visitor)
