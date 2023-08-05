
import typing as t

from nr.util.generic import T, K, V

T_ChainDict = t.TypeVar('T_ChainDict', bound='ChainDict')
_can_iteritems = lambda x: hasattr(x, 'items')


class ChainDict(t.MutableMapping[K, V]):
  """
  A dictionary that wraps a list of dictionaries. Except for the first dictionary passed into the #ChainDict
  constructor, none will be mutated through any actions on this dictionary.
  """

  def __init__(self, main: t.MutableMapping[K, V], *others: t.Mapping[K, V]) -> None:
    self._main = main
    self._dicts: t.List[t.Mapping[K, V]] = [t.cast(t.Mapping[K, V], main)] + list(others)
    self._deleted: t.Set[K] = set()
    self._in_repr = False

  def __contains__(self, key: t.Any) -> bool:
    if key not in self._deleted:
      for d in self._dicts:
        if key in d:
          return True
    return False

  def __getitem__(self, key: K) -> V:
    if key not in self._deleted:
      for d in self._dicts:
        try: return d[key]
        except KeyError: pass
    raise KeyError(key)

  def __setitem__(self, key: K, value: V) -> None:
    self._main[key] = value
    self._deleted.discard(key)

  def __delitem__(self, key: K) -> None:
    if key not in self:
      raise KeyError(key)
    try: self._main.pop(key)
    except KeyError: pass
    self._deleted.add(key)

  def __iter__(self) -> t.Iterator[K]:
    return self.keys()

  def __len__(self) -> int:
    return sum(1 for x in self.keys())

  def __repr__(self) -> str:
    if self._in_repr:
      return 'ChainDict(...)'
    else:
      self._in_repr = True
      try:
        return 'ChainDict({})'.format(dict(self.items()))
      finally:
        self._in_repr = False

  def __eq__(self, other: t.Any) -> bool:
    return dict(self.items()) == other

  def __ne__(self, other: t.Any) -> bool:
    return not (self == other)

  @t.overload
  def get(self, key: K) -> t.Optional[V]: ...

  @t.overload
  def get(self, key: K, default: T) -> t.Union[V, T]: ...

  def get(self, key, default=None):
    try:
      return self[key]
    except KeyError:
      return default

  @t.overload  # type: ignore  # TODO (NiklasRosenstein)
  def pop(self, key: K) -> V: ...

  @t.overload
  def pop(self, key: K, default: t.Union[V, T]) -> t.Union[V, T]: ...

  def pop(self, key, default=NotImplemented):
    try:
      value = self[key]
    except KeyError:
      if default is NotImplemented:
        raise KeyError(key)
      return default
    else:
      del self[key]
    return value

  def popitem(self) -> t.Tuple[K, V]:
    if self._main:
      key, value = self._main.popitem()
      self._deleted.add(key)
      return key, value
    for d in self._dicts:
      for key in d.keys():
        if key not in self._deleted:
          self._deleted.add(key)
          return key, d[key]
    raise KeyError('popitem(): dictionary is empty')

  def clear(self) -> None:
    self._main.clear()
    self._deleted.update(self.keys())

  def copy(self: T_ChainDict) -> T_ChainDict:
    return type(self)(self._main, *self._dicts[1:])

  def setdefault(self, key: K, value: V) -> V:  # type: ignore  # TODO (NiklasRosenstein)
    try:
      return self[key]
    except KeyError:
      self[key] = value
      return value

  def update(self, E: t.Mapping[K, V], *F: t.Mapping[K, V]) -> None:  # type: ignore  # TODO (NiklasRosenstein)
    if _can_iteritems(E):
      for k, v in E.items():
        self[k] = v
    else:
      for k in E.keys():
        self[k] = E[k]
    for Fv in F:
      for k, v in Fv.items():
        self[k] = v

  def keys(self):
    seen = set()
    for d in self._dicts:
      for key in d.keys():
        if key not in seen and key not in self._deleted:
          yield key
          seen.add(key)

  def values(self):
    seen = set()
    for d in self._dicts:
      for key, value in d.items():
        if key not in seen and key not in self._deleted:
          yield value
          seen.add(key)

  def items(self):
    seen = set()
    for d in self._dicts:
      for key, value in d.items():
        if key not in seen and key not in self._deleted:
          yield key, value
          seen.add(key)
