import typing

from .binary_search import binary_search


def doubling_search(
    predicate: typing.Callable[[int], bool],
    lower_bound: int = 0,
) -> int:
    """
    Find the positive integer threshold below which a search criteria is never
    satisfied and above which it is always satisfied.

    Parameters
    ----------
    predicate : callable object
        Returns whether an integer value satisfies the search criteria.
    lower_bound : int, optional
        The initial guess. Should be less than or equal to the first value that
        satsfies the search criteria. Used for recursion. Default is 0.

    Returns
    -------
    threshold
        The lowest integer value that satisfies the search criteria.
    """

    assert lower_bound >= 0, lower_bound

    bound = 1
    while not predicate(lower_bound + bound):
        bound *= 2

    prev_bound = bound // 2
    prev_guess = lower_bound + prev_bound
    return binary_search(predicate, prev_guess, lower_bound + bound)
