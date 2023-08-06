def greatest_common_divisor(a: int, b: int):
    if b > 0:
        return greatest_common_divisor(b, a % b)
    else:
        return a
