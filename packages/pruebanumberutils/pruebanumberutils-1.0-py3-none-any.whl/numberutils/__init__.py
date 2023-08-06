def suma_enteros(a, b):
	return a+b

def resta_enteros(a, b):
	return a-b

def producto_enteros(a,b):
	return a*b

# 5! = 1*2*3*4*5
def factorial(n):
	if(n == 0):
		return 1
	
	resultado = 1
	for i in range(1, n+1):
		resultado = resultado * i

	return resultado 

def listar_n_pares(n):
	pares = []

	i = 0
	while(i <= n):
		if(i % 2 == 0):
			pares.append(i)
		i += 1

	return pares