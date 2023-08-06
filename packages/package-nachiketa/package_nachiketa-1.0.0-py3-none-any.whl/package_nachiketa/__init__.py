def fibo(num):
    a = 0
    b = 1

    if num > 1:
        for _ in range(1, num):
            t = a
            a = b
            b = a + t

    print(num, "th fibonacci number is :")

    return a
