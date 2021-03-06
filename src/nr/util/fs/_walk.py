
import typing as t
from pathlib import Path


def recurse_directory(path: Path) -> t.Iterator[Path]:
  for item in path.iterdir():
    yield item
    if item.is_dir():
      yield from recurse_directory(item)


def walk_up(path: Path) -> t.Iterator[Path]:
  prev = None
  while path != prev:
    yield path
    prev, path = path, path.parent
