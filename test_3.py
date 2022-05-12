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
        andere_perms = permutaties(left + right)
        for rest in andere_perms:
            perms.append([lijst[i]] + rest)
    return perms
permutaties([1,2,3])