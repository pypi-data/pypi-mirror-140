
import typing as t
import typing_extensions as te

from nr.util.generic import T_contra


class Predicate(te.Protocol[T_contra]):

  def __call__(self, obj: T_contra) -> bool:
    ...
