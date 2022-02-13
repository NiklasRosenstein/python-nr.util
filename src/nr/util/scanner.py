
import typing as t
from nr.util.generic import T


class Scanner(t.Generic[T]):
  """ The scanner is a utility class to walk over the items of a sequence in an easy to use manner. """

  def __init__(self, sequence: t.Sequence[T]) -> None:
    self.sequence = sequence
    self.index = 0

  def __bool__(self) -> bool:
    """ Returns `True` if the scanner is pointing to an element in the sequence, `False` if not. """
    return self.index < len(self.sequence)

  @property
  def current(self) -> T:
    """ Returns the item in the sequence that the scanner is currently pointing to. """
    return self.sequence[self.index]

  def has_next(self) -> bool:
    """ Returns `True` if calling {@meth next()} will be successful, i.e. if there is a next element that the scanner
    can move to. """
    return self.index < len(self.sequence) - 1

  def next(self) -> T:
    """ Returns the next element in the sequence. Note that this cannot be used to advance the scanner beyond the
    end of the sequence; use #advance() instead. """
    if self.has_next():
      self.index += 1
      return self.sequence[self.index]
    else:
      raise ValueError('no next element for the scanner to move to')

  def advance(self) -> None:
    if self:
      self.index += 1

  def ensure_advancing(self, strict_forward: bool = True) -> t.Iterator[T]:
    """ A utility iterator that yields the current line of the scanner at each step of the iteration. After each
    step, it ensures that the Scanner was at least moved forward by one index, or modified at all if *strict* is
    disabled. """

    while self:
      index = self.index
      yield self.current
      if self.index == index:
        raise RuntimeError('scanner was not advanced')
      if strict_forward and self.index < index:
        raise RuntimeError('scanner as moved backwards but strict_forward is enabled')
