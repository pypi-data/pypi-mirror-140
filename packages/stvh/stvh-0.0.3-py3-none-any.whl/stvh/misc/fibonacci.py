def fibonacci(inp: int) -> list[int]:
    """Fibonacci

    Args:
        inp (int): TODO

    Returns:
        ret (list[int]): list of fibonacci numbers
    """
    if inp < 0:
        raise ValueError

    if inp == 0:
        return [0]

    if inp == 1:
        return [0, 1]

    ret = [0, 1]

    for _ in range(2, inp + 1):
        ret.append(ret[-2] + ret[-1])

    return ret
