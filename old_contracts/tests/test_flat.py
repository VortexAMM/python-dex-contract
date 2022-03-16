# import math

# X = 10 ** 10
# Y = 10 ** 10
# dX = 10 ** 5
# dX_deducted = dX * 9972 // 10000
# dY0 = 0


def u(X, Y): return ((X + Y) ** 8 - (X - Y) ** 8)
def du_dy(X, Y): return (8 * (X + Y) ** 7 + 8 * (X - Y) ** 7)


def newton(x, y, dx, dy, v, n):
    for i in range(n):
        V = u(x + dx, y - dy)
        dV = du_dy(x + dx, y - dy)
        dy = dy + (V - v) // dV
        v = V
        i -= 1
    return(dy)


# xtz_bought = (dX * 9972 * Y) // (
#     X * 10000 + (dX * 9972))

# print(xtz_bought)


# dY = newton(X, Y, dX_deducted, dY0, u(X, Y), 5)
# print(dY)

# dX1 = 10 ** 8 // 2
# dX2 = 10 ** 8 // 2
# dX = dX1 + dX2
