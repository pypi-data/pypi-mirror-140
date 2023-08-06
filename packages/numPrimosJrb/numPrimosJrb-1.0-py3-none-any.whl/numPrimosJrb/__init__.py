def num_primos(n):
    numerosPrimos=[]
    for i in range(2,n+1):
        if i>=2:
            cont=0
            for j in range(2,i):
                if (i%j==0): 
                    cont+=1
                    break
            if cont==0: 
                numerosPrimos.append(i) 
    print("Numeros primos son : ",numerosPrimos) 

numero=int(input("¿HASTA QUE NUMERO QUIERES SABER SI SON NUMEROS PRIMOS?\t"))
num_primos(numero)