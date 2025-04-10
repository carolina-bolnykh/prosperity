crates = [(10, 1), (80, 6), (37, 3), (90, 10), (31, 2), (17, 1), (50, 4), (20, 2), (73, 4), (89, 8)]

best = -1
c = ()

least = 10000

for i in range(len(crates)):
    for j in range(len(crates)):
        if i == j:
            continue
        value = (crates[i][0] * least) / (crates[i][1] + 1)
        value += (crates[j][0] * least) / (crates[j][1] + 1)
        value -= 50000
        if value > best:
            best = value
            c = (i, j)

print(best)
print(crates[c[0]], crates[c[1]])
        
