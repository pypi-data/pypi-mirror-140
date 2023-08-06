import numpy as np
import pandas as pd


def calcula_serie_velocidad(arreglo_tiempo,
                            posiciones_x, posiciones_y):
    tiempos = arreglo_tiempo
    longitud_movimientos = len(posiciones_x)
    lista_velocidad = np.zeros(longitud_movimientos)

    for i in range(1, longitud_movimientos):
        valor_tiempo = tiempos[i] - tiempos[i - 1]
        if np.isnan(posiciones_x.iloc[i - 1]):
            lista_velocidad[i - 1] == 0
        elif np.isnan(posiciones_x.iloc[i]):
            lista_velocidad[i - 1] == 0
        else:
            lista_velocidad[i - 1] = (((posiciones_x.iloc[i] - posiciones_x.iloc[i - 1]) ** 2 + (
                    posiciones_y.iloc[i] - posiciones_y.iloc[i - 1]) ** 2) ** 0.5) / valor_tiempo
    serie_velocidad = pd.Series(lista_velocidad)
    velocidad_maxima = round(serie_velocidad.max(), 3)

    return serie_velocidad


def calcula_serie_aceleracion(arreglo_tiempo,
                              serie_velocidad):
    tiempos = arreglo_tiempo
    longitud_velocidad = serie_velocidad.size
    lista_aceleracion = np.zeros(longitud_velocidad)

    for i in range(1, longitud_velocidad):
        valor_tiempo = tiempos[i] - tiempos[i - 1]
        lista_aceleracion[i - 1] =\
            (serie_velocidad.iloc[i] - serie_velocidad.iloc[i - 1]) / valor_tiempo

    serie_aceleracion = pd.Series(lista_aceleracion)
    aceleracion_maxima = round(serie_aceleracion.max(), 3)
    return serie_aceleracion, aceleracion_maxima


def obtener_arreglo_promediado(serie_a_promediar, cantidad_datos_promedio):
    longitud_serie_original = serie_a_promediar.size
    posicion_extra = 0
    if longitud_serie_original % cantidad_datos_promedio > 0:
        posicion_extra = 1
    longitud_arreglo_promediado =\
        int(longitud_serie_original / cantidad_datos_promedio + posicion_extra)
    arreglo_promediado = np.zeros(longitud_arreglo_promediado)
    for i in range(0, longitud_arreglo_promediado - 1):
        for j in range(cantidad_datos_promedio):
            arreglo_promediado[i] = \
                arreglo_promediado[i] + serie_a_promediar[cantidad_datos_promedio*i + j]
        arreglo_promediado[i] /= cantidad_datos_promedio
    for j in range(longitud_serie_original % cantidad_datos_promedio):
        arreglo_promediado[-1] = \
            serie_a_promediar.iloc[cantidad_datos_promedio*(longitud_arreglo_promediado-1) + j]
    serie_promediada = pd.Series(serie_a_promediar)
    return serie_promediada
