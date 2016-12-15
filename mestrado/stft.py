#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import numpy as np
import scipy.signal


def stft(signal, wsize, hop):
    """Implementação da Transformada Curta de Fourier (STFT).

    Parâmetros:
    -----------
    signal: array_like
        sinal a ser processado.
    wsize: int
        tamanho das janelas (em número de amostras).
    hop: int
        número de amostras para deslocamento entre janelas.

    Retorno:
    --------
    (list, list):
        consiste em uma tupla de duas dimensões. A primeira dimensão contém os
        coeficientes da transformada (linha: janela; coluna:frequência). A
        segunda dimensão corresponde à amostra que a janela representa (centro
        da janela).
    """
    logging.debug("Calculando limites das janelas.")

    wleft = len(signal)-wsize+1  # limite máximo para índice inferior da janela
    wright = len(signal)+1       # limite máximo para índice superior da janela

    left = range(0, wleft, hop)         # indices inferiores das janelas
    right = range(wsize, wright, hop)   # indices superiores das janelas

    csize = (wsize/2) + 1
    windex_list = np.zeros(len(left))   # índices das janelas (amostra)

    # Armazena os coeficientes da STFT.
    # Cada linha corresponde aos coeficientes de uma janela
    stft_coef = np.zeros((len(left), csize), dtype=complex)

    logging.debug("Criando janela gaussiana.")
    g = scipy.signal.kaiser(wsize, 14)

    for index, (lb, rb) in enumerate(zip(left, right)):
        wi = (lb+rb)/2
        windex_list[index] = wi

        logging.debug(("Calculando STFT da janela {} [{}:{}]"
                       "".format(wi, lb, rb)))

        window = [i*j for i, j in zip(g, signal[lb:rb])]
        wi_coef = np.fft.rfft(window)
        stft_coef[index] = wi_coef

    return stft_coef, windex_list


def stftfreq(wsize, sfreq):
    """Calcula as frequências extraídas por *stft.stft*, retornando uma lista.

    Função que retorna as frequências representadas pelos coeficientes da
    Transformada de Fourier em *stft.stft*.

    Parâmetros:
    -----------
    wsize: int
        tamanho das janelas usadas na STFT (em amostras).
    sfreq: float
        frequência de amostragem do sinal (em Hertz).

    Retorno:
    --------
    list:
        lista de frequências correspondentes aos coeficientes da Transformada
        de Fourier para as janelas.
"""
    freq = np.fft.rfftfreq(wsize, d=1.0/sfreq)
    return freq
