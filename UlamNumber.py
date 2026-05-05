def initUlamSeq(n):
    ulamList = [1, 2]
    ulamSet = {1, 2}
    candidate = 3
    while len(ulamList) < n:
        pairCount = sum(
            1 for a in ulamList if a < candidate - a and (candidate - a) in ulamSet
        )
        if pairCount == 1:
            ulamList.append(candidate)
            ulamSet.add(candidate)
        candidate += 1
    return ulamList

n = input("Enter n for Ulam(n): ")
ulamList = initUlamSeq(int(n))
print(ulamList)
input("Enter to continue...")
