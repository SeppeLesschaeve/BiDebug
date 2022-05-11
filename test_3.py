def permutaties(lijst):
    if lijst == []:
        return []
    perms = []
    for i in range(len(lijst)):
        left = []
        for j in range(i):
            left.append(lijst[j])
        right = []
        for j in range(i+1,len(lijst)):
            right.append(lijst[j])
        for rest in permutaties(left + right):
            perms.append([lijst[i]] + rest)
    return perms
permutaties([1,2,3])