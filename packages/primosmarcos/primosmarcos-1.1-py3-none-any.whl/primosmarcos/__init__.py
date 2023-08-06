

def es_primo(num):
    if num <2:
        return False
    for n in range(2, num):
        if num % n == 0:
            #print("No es primo", n, "es divisor")
            return False
    #print("Es primo")
    return True

def lista_primos(num):
    listado =[]
    for i in range(2,num+1):
        if es_primo(i):
            listado.append(i)

    return listado



#print("Introduce un número:")
#numero = int(input())

#print(lista_primos(numero))