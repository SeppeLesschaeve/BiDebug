def som(lijst):
    if len(lijst) <= 1:
        return 0
    rest = []
    for i in range(1,len(lijst)):
        rest.append(lijst[i])
    return lijst[0] + som(rest)
print(som([1,2,3]))