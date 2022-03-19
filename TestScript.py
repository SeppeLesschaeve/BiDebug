a = 1
b = 2
ll = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]


def div(d1, d2):
    return d1 / d2


def main():
    for x in ll:
        i = 0
        while x > 4:
            x = div(x, 2) - i
    c = 2
    while c > 0:
        c -= 1
        if c == 0:
            break
        else:
            global a
            a += 1


main()
