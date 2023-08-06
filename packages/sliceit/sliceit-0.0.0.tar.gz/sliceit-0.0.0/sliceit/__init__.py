"""
sliceit
--------
Dynamically sized slice views which avoid storing their own data.

The builtin list, tuple, str, etc., create copies when sliced.
This is to allow all of the unnecessary memory to be freed if it
is no longer needed. In some cases, the opposite problem occurs,
where none of the memory needs to be freed anyways, meaning slices
simply take up more space than necessary.

Some data structures provide slicing views already, such as:
- numpy
- pandas
- tensorflow
- and many other data science packages

If these packages already fit your needs, consider using them instead.

What's different?
------------------
`sliceit` provides sliceable views any `Sequence` (or `MutableSequence`),
meaning it works for lists, tuples, strings, etc., and can also be used
as an easy way to implement slicing for custom classes.

Furthermore, `sliceit` uses lazily evaluated slices. This means the
underlying data is free to change size as much as it wants. The catch
is that some objects may raise runtime errors if you try iterating
over them at the same time.

Unlike some, `sliceit` is also recursively sliceable and supports mutations,
although modifying slices may in some cases be unintuitive.

Examples
---------

```python
from sliceit import sliceit

print("Create a slice view of some data.")
L = list(range(100))
S = sliceit(L)[::-10]
print(f"S = {S}")

print()

print("Slices act as a view over the data.")
print(f"list(S) = {list(S)}")
L[0] = -10
print(f"L[0] := -10")
print(f"list(S) = {list(S)}")
L[0] = 0
print(f"L[0] := 0")
print(f"list(S) = {list(S)}")

print()

print("They can be looped over or indexed as you would expect.")
print(f"[x for x in S] = {[x for x in S]}")
print(f"S[0] = {S[0]})

print()

print("Slices are compiled together whenever possible.")
print(f"S[::2] = {S[::2]}")
print(f"S[:5] = {S[:5]}")
print(f"S[5:] = {S[5:]}")

print()

print("If the data is mutable, the slice is mutable.")
S[0] = 0
print("S[0] := 0")
print(f"L[-10] = {L[-10]}")
S[0] = 90
print("S[0] := 90")
print(f"L[-10] = {L[-10]}")
```
"""
from ._slice_view import MutableSliceView, SliceView, sliceit

__all__ = ["MutableSliceView", "SliceView", "sliceit"]
__version__ = "0.0.0"
