import numpy as np


def distancia_arreglos_pendientes(arreglo_pendiente_1, arreglo_pendiente_2):
    return (1/2)*(1 - (np.dot(arreglo_pendiente_1, arreglo_pendiente_2) /
                       (np.dot(a=np.abs(arreglo_pendiente_1), b=np.abs(arreglo_pendiente_2)))))


def genera_pendiente_con_funcion_signo(arreglo_pendiente, epsilon):
    arreglo_resultado = []
    for valor in arreglo_pendiente:
        signo = funcion_signo(valor, epsilon)
        arreglo_resultado.append(signo)
    return arreglo_resultado


def funcion_signo(valor, epsilon):
    if valor > epsilon:
        return 1
    elif -epsilon <= valor <= epsilon:
        return 0
    elif valor < -epsilon:
        return -1

