#!/usr/bin/env python
# -*- coding: utf-8 -*-

import itertools as itt
import logging
import numpy as np

from mestrado import plotModels as pm

def plotCHBMITSignal(raw, file_pattern, ext_args=None):
    logging.debug("Executando plotagem do sinal.")

    logging.debug("Calculando média dos canais.")
    avg = np.mean(raw._data, axis=0)

    logging.debug("Criando lista (iterador) com canais e média.")
    channel_list = itt.chain(raw._data, [avg])
    channel_len = len(raw._data) + 1

    logging.debug("Criando marcações de eventos (crises).")
    events = None
    if raw.annotations:
        annot = raw.annotations
        elabel = annot.description[0]
        estart = annot.onset*raw.info['sfreq']
        eend = annot.duration*raw.info['sfreq'] + estart
        events = [pm.createEvent('Seizure', estart, eend, 'red')]

    logging.debug(("Definindo função de formatação dos rótulos dos traços nos "
                   "eixos x e y."))
    y_fmt = lambda x, y: "{}$\mu$V".format(int(x*1e6))
    x_fmt = lambda x, y: "{:.2f}".format(x/(raw.info['sfreq']*60))

    logging.debug("Gerando plot.")
    title = "Signal {}".format(file_pattern)
    ylabels = raw.ch_names
    ylabels.append('AVG')
    xlabel = 'Time [minutes]'

    pm.plotChannels(channel_list, signal_len=channel_len, events=events,
            sharey=True, xformatter=x_fmt, yformatter=y_fmt, ytick_bins=5, title=title,
            xlabel=xlabel, ylabel=ylabels, xtick_bins=10, save_path=file_pattern, dpi=600,
            linewidth=0.1, borderwidth=0.2, xtick_size=2, ytick_size=2)

    logging.debug("Finalizando plotagem: {}".format(file_pattern))


def plotCHBMITWindowedSignals():
    pass

def plotCHBMITSizures(raw, file_pattern, plt_args=None ):
    pass
