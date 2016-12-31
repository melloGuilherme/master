#!/usr/bin/env python
# -*- coding: utf-8 -*-

import itertools as itt
import logging
import numpy as np

from mestrado import pathManipulation as pm
from mestrado import plotModels as pltm


def applyFourier(raw, fpattern, ext_args=None):
    """Script para execução da transformada de fourier na base chbmit.

    Script para a plotagem da transformada de fourier de um determinado sinal,
    passado em *raw*. São gerados gráficos para o sinal inteiro, e por bandas.
    Aqui, as bandas são descridas por delta (0~4Hz), teta (4~8Hz), alfa (8~14),
    beta (14~30Hz) e gama (>30Hz).

    Parâmetros:
    -----------
    raw: mne.Raw
        objeto Raw da biblioteca mne, contendo informações sobre o sinal.
    fpattern: str
        string contendo o padrão para salvar os gráficos gerados.
    ext_args: None
        este parâmetro não é utilizado dentro desta função, porém, ao usar a
        função *defaultScript* para executar a transformada de fourier, devem
        ser passados como argumentos extras os valores '1Delta', '2Tetha',
        '3Alpha', '4Beta' e '5Gamma'.
    """
    logging.info("Executando Fourier.")

    # manipulação dos sinais
    data = raw._data
    avg = np.mean(data, axis=0)

    # cria uma lista com todos os sinais
    channels = itt.chain(data, [avg])

    # claculo da transformada de fourier
    pspect = []
    for channel in channels:
        ft = np.fft.rfft(channel)       # coeficientes positivos
        ps = np.power(np.abs(ft), 2)    # espectro de potência
        pspect.append(ps)

    pspect = np.array(pspect)

    d = 1./raw.info['sfreq']
    freq = np.fft.rfftfreq(len(raw), d=d)

    logging.debug("Número de Espectros calculados: {}"
                  "".format(len(pspect)))
    logging.debug("Número de Coeficientes nos espectros: {}"
                  "".format(len(pspect[0])))
    logging.debug("Número de frequências calculadas (rfftfreq): {}"
                  "".format(len(freq)))

    logging.debug("Selecionando Faixas de Frequências.")
    npland = np.logical_and     # shotcut
    e = 0.0000001               # error
    # delta waves [0~4Hz]
    delta = (np.where(npland(freq >= (0-e), freq <= (0+e)))[0][0],
             np.where(npland(freq >= (4-e), freq <= (4+e)))[0][0])

    # theta waves [4~8Hz]
    theta = (np.where(npland(freq >= (4-e), freq <= (4+e)))[0][0],
             np.where(npland(freq >= (8-e), freq <= (8+e)))[0][0])

    # alpha waves [8~14Hz]
    alpha = (np.where(npland(freq >= (8-e), freq <= (8+e)))[0][0],
             np.where(npland(freq >= (14-e), freq <= (14+e)))[0][0])

    # beta waves [14~30Hz]
    beta = (np.where(npland(freq >= (14-e), freq <= (14+e)))[0][0],
            np.where(npland(freq >= (30-e), freq <= (30+e)))[0][0])

    # gamma waves [>30Hz]
    gamma = (np.where(npland(freq >= (30-e), freq <= (30+e)))[0][0],
             len(freq))

    wave_band = [(0, len(freq))]    # all freqs
    wave_band.append(delta)
    wave_band.append(theta)
    wave_band.append(alpha)
    wave_band.append(beta)
    wave_band.append(gamma)

    logging.info("Calculando parâmetros de plotagem.")
    ylabel_list = raw.ch_names
    ylabel_list.append("AVG")
    xlabel = "Frequências (Hz)"
    title_pattern = "Espectro de Potência: {}"

    band_patterns = ['', '1Delta', '2Theta', '3Alpha', '4Beta', '5Gamma']
    for (ws, wf), bpattern in zip(wave_band, band_patterns):
        it = [pspect[i][ws:wf] for i in range(len(pspect))]
        img_save_path = fpattern.format(bpattern)

        flabel = pm.extractFileLabel(img_save_path)
        title = title_pattern.format(flabel)

        logging.info("Gerando plot: {}".format(img_save_path))
        pltm.plotChannels(it, signal_time=freq[ws:wf], dpi=600, title=title,
                          ylabel=ylabel_list, linewidth=0.2, borderwidth=0.2,
                          ytickline_visible=True, xlabel=xlabel, xtick_size=1,
                          yticklabel_visible=True, ytick_bins=4, figsize=None,
                          save_path=img_save_path, ytick_size=1)

        logging.debug("Imagem salva em {}".format(img_save_path))


# TODO: Apagar esta parte antes de dar commit
# if __name__ == "__main__":
#     from mestrado import argline
#     from mestrado.chbmit import fourier
#     from mestrado.chbmit import utils
#
#     argline.config()
#
#     plabel = 'chb01'
#     edf_label = '{}_01'.format(plabel)
#     sum_label = '{}-summary'.format(plabel)
#
#     dataset_path = '/home/mello/Biblioteca/datasets/chbmit'
#     edf_path = '{}/{}/{}.edf'.format(dataset_path, plabel, edf_label)
#     sum_path = '{}/{}/{}.txt'.format(dataset_path, plabel, sum_label)
#
#     sum_dict = utils.summaryFileParser(sum_path)
#     raw = utils.openEDF(edf_path, sum_dict)
#
#     fpattern = './out/{}/{}_FT{}.png'.format(plabel, '{}','{}')
#     eargs = ['', '1Delta', '2Theta', '3Alpha', '4Beta', '5Gamma']
#
#     applyFourier(raw, fpattern, ext_args=eargs)
