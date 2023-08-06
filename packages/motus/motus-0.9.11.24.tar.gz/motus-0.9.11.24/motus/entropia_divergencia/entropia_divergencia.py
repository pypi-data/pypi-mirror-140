import numpy as np
import scipy.stats as st


def agrega_categoria_entropia(diccionario_entropia, categoria, datos):
    print("Agrego categoria de entropia: ")
    print("--------------------------------------------------------------")
    print("Diccionario:", diccionario_entropia)
    print("Categoria", categoria)
    print("Datos:", datos)
    nuevos_datos = np.array(datos)
    if categoria not in diccionario_entropia:
        diccionario_entropia[categoria] = st.entropy(nuevos_datos)
    print("Nuevo diccionario: ", diccionario_entropia)

def agrega_categoria_entropia_aproximada(diccionario_entropia,
                                         categoria,
                                         datos,
                                         tamanio_vectorial,
                                         traslape):
    print("Agrego categoria de entropia aproximada: ")
    print("--------------------------------------------------------------")
    print("Diccionario:", diccionario_entropia)
    print("Categoria", categoria)
    print("Datos:", datos)
    nuevos_datos = np.array(datos)
    if categoria not in diccionario_entropia:
        print("Procesando informacion")
        diccionario_entropia[categoria] = ApEn(nuevos_datos, tamanio_vectorial, traslape)
    print("Nuevo diccionario: ", diccionario_entropia)


def modificar_arreglo_para_evitar_divergencia_infinita(datos):
    nuevos_datos = np.copy(datos)
    indices_con_valores_0 = np.argwhere(nuevos_datos == 0)

    for indice in indices_con_valores_0:
        nuevos_datos[indice] = 1

    return nuevos_datos


def calcula_divergencia_de_2_arreglos(pk, qk):
    nuevo_qk = modificar_arreglo_para_evitar_divergencia_infinita(qk)
    divergencia = st.entropy(pk, nuevo_qk)
    return divergencia


def calcula_divergencias_de_lista_arreglos(lista_arreglos):

    resultados_divergencia = []

    for i in range(0, len(lista_arreglos) - 1):
        pk = lista_arreglos[i]
        qk = lista_arreglos[i+1]

        divergencia_pk_qk = calcula_divergencia_de_2_arreglos(pk, qk)

        resultados_divergencia.append(divergencia_pk_qk)

    return resultados_divergencia


def ApEn(U, m, r) -> float:
    """Approximate_entropy."""

    def _maxdist(x_i, x_j):
        return max([abs(ua - va) for ua, va in zip(x_i, x_j)])

    def _phi(m):
        x = [[U[j] for j in range(i, i + m - 1 + 1)] for i in range(N - m + 1)]
        C = [
            len([1 for x_j in x if _maxdist(x_i, x_j) <= r]) / (N - m + 1.0)
            for x_i in x
        ]
        return (N - m + 1.0) ** (-1) * sum(np.log(C))

    print("Datos en entropia aprox: ", U)

    N = len(U)

    return _phi(m) - _phi(m + 1)