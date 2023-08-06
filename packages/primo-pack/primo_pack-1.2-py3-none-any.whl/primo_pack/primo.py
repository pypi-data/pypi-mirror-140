# -*- coding: utf-8 -*-
"""
Created on Mon Feb 28 19:30:58 2022

@author: Mauro
"""

"""
En matemáticas, un número primo es un número natural mayor que 1 que tiene 
únicamente dos divisores positivos distintos: él mismo y el 1

Por el contrario, los números compuestos son los números naturales que tienen 
algún divisor natural aparte de sí mismos y del 1, y, por lo tanto, 
pueden factorizarse. 

El número 1, por convenio, no se considera ni primo ni compuesto.
"""

#Primero defino el nombre de la función que acepta un parámetro de entrada N
def primo(n):   
    #Recorremos el bucle desde 2 hasta el número que nos indique el usuario  N
    # N+1 es para que e cuente el último número que ingreso
	for i in range(2, n+1):
        #Para cada interacción comenzamos definiendo la variable ES_PRIMO como TRUE
		es_primo = True      
        #Realizamos una segunda interacción desde dos hasta el número que estemos recorriendo
		for j in range(2, i):
            #Si el residuo de dividir I entre J es cero
			if(i%j == 0):
                #Como tiene divisores no es un número primo
				es_primo = False
		if(es_primo):           
			print(f"{i} es primo")
            