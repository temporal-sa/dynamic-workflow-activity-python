from typing import Sequence


async def multiply(xs: Sequence[int]) -> int:
    result = 1
    for x in xs:
        result *= x
    return result
