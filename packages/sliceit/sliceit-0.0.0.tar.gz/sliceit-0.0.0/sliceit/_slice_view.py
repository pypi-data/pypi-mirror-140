from __future__ import annotations
from collections.abc import MutableSequence, Sequence
from itertools import islice
from typing import Generic, Iterator, SupportsIndex, Tuple, TypeVar, Union, overload

import operator

__all__ = ["MutableSliceView", "SliceView", "sliceit"]

T = TypeVar("T")

def slice_repr(s: slice) -> str:
    """Helper function for printing slices."""
    start = "" if s.start is None else repr(s.start)
    stop = "" if s.stop is None else repr(s.stop)
    step = "" if s.step is None else ":" + repr(s.step)
    return f"[{start}:{stop}{step}]"

@overload
def sliceit(seq: MutableSequence[T], /) -> MutableSliceView[T]:
    ...

@overload
def sliceit(seq: Sequence[T], /) -> SliceView[T]:
    ...

def sliceit(seq: Sequence[T], /) -> SliceView[T]:
    """Returns either a mutable slice view or an immutable slice view."""
    if isinstance(seq, MutableSequence):
        return MutableSliceView(seq)
    elif isinstance(seq, Sequence):
        return SliceView(seq)
    else:
        raise TypeError(f"seq must be a sequence, got {seq!r}")


class SliceView(Sequence[T], Generic[T]):
    """
    A slice view contains a reference to other data along
    with the indexes that it references as a slice.

    Unlike normal slicing, slicing a slice view does not
    create a copy of the data, which allows it to run in
    constant time.

    Examples
    ---------
    Slices act as a view over the data.
        >>> L = range(100)
        >>> SliceView(L)[::10]
        SliceView(range(0, 100))[::10]

    They can be looped over or indexed as you would expect.
        >>> list(SliceView(L)[::10])
        [0, 10, 20, 30, 40, 50, 60, 70, 80, 90]
        >>> SliceView(L)[::10][3]
        30

    Slices are compiled together whenever possible.
        >>> SliceView(L)[::10][:5][2:]
        SliceView(range(0, 100))[20:50:10]
        >>> SliceView(L)[::10][2:][:5]
        SliceView(range(0, 100))[20:70:10]
        >>> SliceView(L)[2:][:5][::10]
        SliceView(range(0, 100))[2:7:10]
    """
    _seq: Sequence[T]
    _slices: Tuple[slice, ...]

    __slots__ = ("_seq", "_slices")

    def __init__(self: SliceView[T], seq: Sequence[T], /) -> None:
        if not isinstance(seq, Sequence):
            raise TypeError(f"seq must be a sequence, got {seq!r}")
        self._seq = seq
        self._slices = ()

    @overload
    def __getitem__(self: SliceView[T], index: SupportsIndex, /) -> T:
        ...

    @overload
    def __getitem__(self: SliceView[T], index: slice, /) -> SliceView[T]:
        ...

    @overload
    def __getitem__(self: SliceView[T], index: Union[SupportsIndex, slice], /) -> Union[T, SliceView[T]]:
        ...

    def __getitem__(self: SliceView[T], index: Union[SupportsIndex, slice], /) -> Union[T, SliceView[T]]:
        """Get an item at an index or create another slice."""
        if isinstance(index, SupportsIndex):
            index = operator.index(index)
            # Perform slicing on the `range` to get the indexes.
            indexes = range(len(self._seq))
            for s in self._slices:
                indexes = indexes[s]
            return self._seq[indexes[index]]
        elif not isinstance(index, slice):
            raise TypeError(f"indices must be integers or slices, got {index!r}")
        start = index.start
        stop = index.stop
        step = index.step
        for i in (start, stop, step):
            if i is not None and not isinstance(i, SupportsIndex):
                raise TypeError(f"slice indice {i!r} was not None and could not be interpreted as an integer")
        # Type-cast and simplify cases.
        if step is not None:
            step = operator.index(step)
            if step == 0:
                raise ValueError("slice step cannot be zero")
            elif step == 1:
                step = None
        if start is not None:
            start = operator.index(start)
            if start == 0 and (step is None or step > 0):
                start = None
        if stop is not None:
            stop = operator.index(stop)
            if stop == -1 and (step is not None and step < 0):
                stop = None
        # Slice has no effect.
        if None is start is stop is step:
            return self
        # First slice requires no simplification.
        elif len(self._slices) == 0:
            result = type(self)(self._seq)
            result._slices = (slice(start, stop, step),)
            return result
        result = type(self)(self._seq)
        slices = self._slices
        s = slices[-1]
        # `L[start:stop:step] == L[:stop][start::step]`.
        if stop is not None:
            if s.step is not None:
                stop *= s.step
            if s.start is not None and s.start * stop > 0:
                stop += s.start
            # There was no stop before and the start has the same sign (if it exists).
            if s.stop is None and (s.start is None or s.start * stop > 0):
                slices = (*slices[:-1], slice(s.start, stop, s.step))
            # The stop has the same sign.
            elif s.stop is None or s.stop * stop > 0:
                stop = min(s.stop, stop) if s.step is None or s.step > 0 else max(s.stop, stop)
                slices = (*slices[:-1], slice(s.start, stop, s.step))
            # The stop cannot be merged with the previous slice.
            else:
                if s.start is not None and s.start * stop > 0:
                    stop -= s.start
                if s.step is not None:
                    stop //= s.step
                slices = (*slices, slice(None, stop, None))
        s = self._slices[-1]
        # `L[start::step] == L[start:][::step]`.
        if start is not None:
            if s.step is not None:
                start *= s.step
            # There was no start before.
            if s.start is None:
                slices = (*slices[:-1], slice(start, s.stop, s.step))
            # The starts can be merged if they share the same sign.
            elif s.start * start > 0:
                slices = (*slices[:-1], slice(start + s.start, s.stop, s.step))
            # The starts cannot be merged, separate slicing is necessary.
            else:
                slices = (*slices, slice(start if s.step is None else start // s.step, None, None))
        s = slices[-1]
        # `L[::step]`.
        if step is not None:
            if s.step is not None:
                step *= s.step
            slices = (*slices[:-1], slice(s.start, s.stop, step))
        result._slices = slices
        return result

    def __iter__(self: SliceView[T], /) -> Iterator[T]:
        """Loop over the slice."""
        # Perform slicing on the `range` to get the indexes.
        indexes = range(len(self._seq))
        for s in self._slices:
            indexes = indexes[s]
        # Special cases of `iter(...)` or `reversed(...)`.
        if indexes == range(len(self._seq)):
            return iter(self._seq)
        elif indexes == range(len(self._seq))[::-1]:
            return reversed(self._seq)
        # Special cases of `islice(...)` or `islice(reversed(...))`.
        elif indexes.start == 0 and indexes.step == 1:
            return islice(self._seq, len(indexes))
        elif indexes.start == len(self._seq) - 1 and indexes.step == -1:
            return islice(reversed(self._seq), len(indexes))
        # Brute force indexing.
        else:
            # Zip it with self._seq to allow it to
            # error if size changes while iterating.
            return (self._seq[i] for i, _ in zip(indexes, self._seq))

    def __len__(self: SliceView[T], /) -> int:
        """Returns the length of the slice view."""
        # Perform slicing on the `range` to get the indexes.
        indexes = range(len(self._seq))
        for s in self._slices:
            indexes = indexes[s]
        # The length of the view is the amount of indexes.
        return len(indexes)

    def __repr__(self: SliceView[T], /) -> str:
        """Sliced representation of the view."""
        return f"{type(self).__name__}({self._seq!r})" + "".join([slice_repr(s) for s in self._slices])


class MutableSliceView(SliceView[T], MutableSequence[T], Generic[T]):
    """
    A mutable slice view allows deletion and mutations
    of slices which affect the original data.

    Examples
    ---------
    Mutable slice views are created just like immutable slice views.
        >>> L = list(range(10))
        >>> S = MutableSliceView(L)[::-1]
        >>> print(*S)
        9 8 7 6 5 4 3 2 1 0

    Mutable slice views may be updated, affecting the original data.
        >>> S[0] = 10
        >>> print(*S)
        10 8 7 6 5 4 3 2 1 0
        >>> print(*L)
        0 1 2 3 4 5 6 7 8 10

    Deletions and insertions may be done, affecting the original data.
        >>> del S[0]
        >>> print(*S)
        8 7 6 5 4 3 2 1 0
        >>> print(*L)
        0 1 2 3 4 5 6 7 8

        >>> S.append(-1)
        >>> print(*S)
        8 7 6 5 4 3 2 1 0 -1
        >>> print(*L)
        -1 0 1 2 3 4 5 6 7 8

    NOTE: Slice assignments and deletions only work if the original data supports it.
          This may change in the future.
    """
    _seq: MutableSequence[T]

    __slots__ = ()

    def __init__(self: MutableSliceView[T], seq: MutableSequence[T], /) -> None:
        if not isinstance(seq, MutableSequence):
            raise TypeError(f"seq must be a mutable sequence, got {seq!r}")
        super().__init__(seq)

    def __delitem__(self: MutableSliceView[T], index: Union[SupportsIndex, slice], /) -> None:
        """Delete an index or slice of the original data. Slicing only works if the original data supports it."""
        if isinstance(index, SupportsIndex):
            index = operator.index(index)
            indexes = range(len(self._seq))
            for s in self._slices:
                indexes = indexes[s]
            if -2 * len(indexes) <= index < len(indexes):
                del self._seq[indexes[index]]
                return
            raise IndexError("index out of range")
        elif not isinstance(index, slice):
            raise TypeError(f"indices must be integers or slices, got {index!r}")
        for i in (index.start, index.stop, index.step):
            if i is not None and not isinstance(i, SupportsIndex):
                raise TypeError(f"slice indice {i!r} was not None and could not be interpreted as an integer")
        # Perform slicing on the `range` to get the indexes.
        indexes = range(len(self._seq))
        for s in self._slices:
            indexes = indexes[s]
        indexes = indexes[index]
        start = indexes.start
        stop = indexes.stop
        step = indexes.step
        if step > 0 and start == 0:
            start = None
        if step > 0 and stop == len(self._seq):
            stop = None
        if step < 0 and start == len(self._seq) - 1:
            start = None
        if step < 0 and stop == -1:
            stop = None
        if step == 1:
            step = None
        del self._seq[start:stop:step]

    @overload
    def __setitem__(self: MutableSliceView[T], index: SupportsIndex, value: T, /) -> None:
        ...

    @overload
    def __setitem__(self: MutableSliceView[T], index: slice, value: Iterable[T], /) -> None:
        ...

    @overload
    def __setitem__(self: MutableSliceView[T], index: Union[SupportsIndex, slice], value: Union[T, Iterable[T]], /) -> None:
        ...

    def __setitem__(self: MutableSliceView[T], index: Union[SupportsIndex, slice], value: Union[T, Iterable[T]], /) -> None:
        """Set an index or slice of the original data. Slicing only works if the original data supports it."""
        if isinstance(index, SupportsIndex):
            index = operator.index(index)
            indexes = range(len(self._seq))
            for s in self._slices:
                indexes = indexes[s]
            if -2 * len(indexes) <= index < len(indexes):
                self._seq[indexes[index]] = value
                return
            raise IndexError("index out of range")
        elif not isinstance(index, slice):
            raise TypeError(f"indices must be integers or slices, got {index!r}")
        for i in (index.start, index.stop, index.step):
            if i is not None and not isinstance(i, SupportsIndex):
                raise TypeError(f"slice indice {i!r} was not None and could not be interpreted as an integer")
        # Perform slicing on the `range` to get the indexes.
        indexes = range(len(self._seq))
        for s in self._slices:
            indexes = indexes[s]
        indexes = indexes[index]
        start = indexes.start
        stop = indexes.stop
        step = indexes.step
        if step > 0 and start == 0:
            start = None
        if step > 0 and stop == len(self._seq):
            stop = None
        if step < 0 and start == len(self._seq) - 1:
            start = None
        if step < 0 and stop == -1:
            stop = None
        if step == 1:
            step = None
        self._seq[start:stop:step] = value

    def clear(self: MutableSliceView[T], /) -> None:
        """Deletes the slice. Equivalent to `del slice_view[:]`."""
        del self[:]

    def insert(self: MutableSliceView[T], index: SupportsIndex, value: T, /) -> None:
        """Insert an item before an index into the original data."""
        if not isinstance(index, SupportsIndex):
            raise TypeError(f"index could not be interpreted as an integer, got {index!r}")
        # Perform slicing on the `range` to get the indexes.
        indexes = range(len(self._seq))
        for s in self._slices:
            indexes = indexes[s]
        # Empty case.
        if len(indexes) == 0:
            if indexes.step > 0:
                self._seq.insert(indexes.start, value)
            else:
                self._seq.insert(indexes.stop + 1 - len(self._seq), value)
        # In bounds.
        elif -2 * len(indexes) <= index < len(indexes):
            if indexes.step > 0:
                self._seq.insert(indexes[index], value)
            else:
                self._seq.insert(indexes[index] - indexes.step - len(self._seq), value)
        # Append.
        elif index * indexes.step > 0:
            if indexes.step > 0:
                self._seq.insert(indexes[-1] + indexes.step, value)
            else:
                self._seq.insert(indexes[0] - indexes.step - len(self._seq), value)
        # Preppend.
        else:
            if indexes.step > 0:
                self._seq.insert(indexes[0], value)
            else:
                self._seq.insert(indexes[-1] + indexes.step - len(self._seq), value)
