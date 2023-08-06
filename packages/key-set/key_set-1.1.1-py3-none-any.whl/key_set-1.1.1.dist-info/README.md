# `key_set`

Python port of [KeySet in TypeScript](https://github.com/eturino/ts-key-set)
and [KeySet in Ruby](https://github.com/eturino/ruby_key_set)

KeySet with 4 classes to represent concepts of All, None, Some, and AllExceptSome, the last 2 with a set of keys, and all with [intersection](#intersectother), [difference](#differenceother), [union](#unionother), [inversion](#invert), and [inclusion](#includeselement) calculations.


## Limitations

- for now, only KeySet of strings
- no ComposedKeySet yet (see [KeySet in TypeScript](https://github.com/eturino/ts-key-set#composedkeyset))

## `KeySetType` enum

Enum that represents the 4 types of KeySets:

- `ALL` represents the entirety of possible keys (`𝕌`)
- `NONE` represents an empty set (`∅`)
- `SOME` represents a concrete set (`A ⊂ 𝕌`)
- `ALL_EXCEPT_SOME` represents the complementary of a set, all the elements except the given
  ones (`A' = {x ∈ 𝕌 | x ∉ A}`) _(see [Complement in Wikipedia](https://en.wikipedia.org/wiki/Complement_set_theory))*

## Creation

Build your KeySets using the build functions

```python
from key_set import build_all, build_none, build_some_or_none, build_all_except_some_or_all

build_all()  # => returns a new instance of KeySetAll
build_none()  # => returns a new instance of KeySetNone

build_some_or_none([])  # returns a new instance of KeySetNone

# returns a new instance of KeySetSome with keys {'a', 'b', 'c'} (in a unique set)
build_some_or_none({'a', 'c', 'b'})
build_some_or_none(['a', 'c', 'b', 'c'])

build_all_except_some_or_all([])  # returns a new instance of KeySetAll

# returns a new instance of KeySetAllExceptSome with keys {'a', 'b', 'c'} (in a unique set)
build_all_except_some_or_all({'a', 'c', 'b'})
build_all_except_some_or_all(['a', 'c', 'b', 'c'])
```

## `KeySet` classes

Methods exposed:

### `key_set_type()`

returns the `KeySetType` enum

### `elements()`

returns the set with the elements. It will be blank for `All` and `None`.

### `represents_xxx()` methods

- `represents_all`: returns True if the KeySet is ALL
- `represents_none`: returns True if the KeySet is NONE
- `represents_some`: returns True if the KeySet is SOME
- `represents_all_except_some`: returns True if the KeySet is ALL_EXCEPT_SOME

### `invert()`

Returns a new KeySet that represents the inverse Set of this one.

- `ALL` <-> `NONE`
- `SOME` <-> `ALL_EXCEPT_SOME`

### `intersect(other)`

Returns a new KeySet with the intersection (A ∩ B) of both Sets: a set that contains the elements included in both sets.

### `union(other)`

Returns a new KeySet with the union (A ∩ B) of both Sets: a set that contains the elements in any of the sets.

### `difference(other)`

Returns a new KeySet with the difference (A - B) of the Sets: a set that contains the elements of A that are not in B.

### `includes(element)`

Returns True if the set that this KeySet represents contains the given element.
