def reference():
    a = [1]
    b = a
    source = {}
    backup = [a, [0,1]]
    for i in range(2):
        if i == 0:
            source['a'] = a
        else:
            source['b'] = b
    source['a'] = backup[1]
    b.append(3)
    print(source['a'])
    print(source['b'])
    print(a)
    print(b)
    source['a'] = backup[0]
    print(source['a'])
    print(source['b'])
    print(a)
    print(b)
    source['b'].append(2)
    print(source['a'])
    print(source['b'])
    print(a)
    print(b)

reference()