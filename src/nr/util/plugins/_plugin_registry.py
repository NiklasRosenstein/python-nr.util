
import typing as t
import warnings

from nr.util.generic import T


class PluginRegistry:
  """ A helper class to register plugins associated with a unique identifier and later access them. """

  def __init__(self) -> None:
    self._groups: dict[t.Hashable, list[t.Any]] = {}

  @t.overload
  def group(self, group: type[T], base_class: T) -> t.Collection[T]: ...

  @t.overload
  def group(self, group: t.Hashable) -> t.Collection[t.Any]: ...

  def group(self, group, base_class=None):
    plugins = self._groups.get(group, [])
    if base_class is None:
      return plugins
    result = []
    for plugin in plugins:
      if not isinstance(plugin, base_class):
        warnings.warn()
    return [p for p in plugins if isinstance(p, base_class)]

  def register(self, group: t.Hashable, name: str, plugin: t.Any) -> None:
    self._groups.setdefault(group, []).append((name, plugin))
