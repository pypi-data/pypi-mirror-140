def primos(a):
    num = int(a)
    primos = []
    count = 0
    
    for i in range(2, num+1):
        for j in range(1, i):
            if(i % j == 0):
                count += 1
        if(count<2):
            primos.append(i)
            
        count = 0
        
    return primos
    
