from typing import Callable

def count_matching(iterable, func: Callable) -> int:
    """Counts occurence that satisfied the condition specified in func and returns it"""
    return sum(map(lambda x: 1 if func(x) else 0, iterable))
