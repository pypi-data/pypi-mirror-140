def numeros_primos(n):
    primos = []
    for i in range(1, n+1):
        if i in (2, 3, 5, 7, 11):
            primos.append(i)
        elif i % 2 == 0:
            pass
        elif i % 3 == 0:
            pass
        elif i % 5 == 0:
            pass
        elif i % 7 == 0:
            pass
        elif i % 11 == 0:
            pass
        else:
            primos.append(i)
    return print(primos)

