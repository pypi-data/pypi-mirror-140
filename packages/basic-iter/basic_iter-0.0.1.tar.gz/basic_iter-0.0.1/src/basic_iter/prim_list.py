from typing import TypeVar, List, Callable, Union, Tuple, Optional, Generic


T = TypeVar('T')
U = TypeVar('U')
S = TypeVar('S')


Predicate = Callable[[T], bool]


class NotFound(Generic[T]):
    def __init__ (self, cond: Union[T, Predicate[T]]):
        self.cond = cond

    def __bool__ (self) -> bool:
        return False

    def __str__ (self) -> str:
        if callable(self.cond):
            return f"Not found for the condition {self.cond}"
        else:
            return f"Not found for the value {self.cond}"


Found = Union[T, NotFound]


def find (e: T, xs: List[T]) -> Found[T]:
    if e in xs:
        return e
    return NotFound(e)


def find_if (p: Predicate[T], xs: List[T]) -> Found[T]:
    for x in xs:
        if p(x):
            return x
    return NotFound(p)


def append (xs: List[T], ys: List[T]) -> List[T]:
    return xs + ys


def map (f: Callable[[T], U], xs: List[T]) -> List[U]:
    return [ f(x) for x in xs ]


def reverse (xs: List[T]) -> List[T]:
    return xs[-1:-len(xs)-1:-1]


def foldl (f: Callable[[T, U], U], e: U, xs: List[T]) -> U:
    acc = e
    for x in xs:
        acc = f (x, acc)
    return acc


def scanl (f: Callable[[T, U], U], e: U, xs: List[T]) -> List[U]:
    acc = e
    res = [acc]
    for x in xs:
        acc = f (x, acc)
        res = [acc] + res
    return reverse(res)


def foldr (f: Callable[[T, U], U], e: U, xs: List[T]) -> U:
    acc = e
    for x in reverse(xs):
        acc = f (x, acc)
    return acc


def scanr (f: Callable[[T, U], U], e: U, xs: List[T]) -> List[U]:
    acc = e
    res = [acc]
    for x in reverse(xs):
        acc = f (x, acc)
        res = [acc] + res
    return res


def zipWith (f: Callable[[T, U], S], xs: List[T], ys: List[U]) -> List[S]:
    assert len(xs) == len(ys), "required to be the same length"
    itx = xs
    ity = ys
    res: List[S] = []
    while itx:
        x = itx[0]
        y = ity[0]
        itx = itx[1:]
        ity = ity[1:]
        res = [f(x, y)] + res
    res.reverse()
    return res


def zip (xs: List[T], ys: List[U]) -> List[Tuple[T, U]]:
    return zipWith(lambda x,y: (x,y), xs, ys)


def unfoldr (f: Callable[[T], Optional[Tuple[U, T]]], init: T) -> List[U]:
    res: List[U] = []
    elm = init
    while True:
        r = f (elm)
        if r:
            (x, e) = r
            res = [x] + res
            elm = e
        else:
            break
    res.reverse()
    return res

