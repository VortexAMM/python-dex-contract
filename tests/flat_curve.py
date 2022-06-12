
def util(x, y):
    plus = x + y
    minus = x - y
    plus_2 = plus * plus
    plus_4 = plus_2 * plus_2
    plus_8 = plus_4 * plus_4
    plus_7 = plus_8 // plus
    minus_2 = minus * minus
    minus_4 = minus_2 * minus_2
    minus_8 = minus_4 * minus_4
    minus_7 = 0 if minus == 0 else minus_8 // minus
    u = abs(plus_8 - minus_8)
    du_dy = 8 * (abs(minus_7 + plus_7))
    return u, du_dy


def newton(x, y, dx, dy, v, n):
    if n == 0:
        return dy
    else:
        new_u, new_du_dy = util(x + dx, abs(y - dy))
        dy = dy + abs((new_u - v) // new_du_dy)
        return(newton(x, y, dx, dy, v, n - 1))
