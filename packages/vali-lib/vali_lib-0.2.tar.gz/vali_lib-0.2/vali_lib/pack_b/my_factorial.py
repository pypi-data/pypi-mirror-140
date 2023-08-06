def factorial(n):
    prod = 1
    for elem in range(1, n+1):
        prod *= elem
    return prod