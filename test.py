def fibonacci(n):
    fib = [1,1]
    while len(fib) < n:
        fib.append(fib[-1] + fib[-2])
    return fib[-1]
fibonacci(3)