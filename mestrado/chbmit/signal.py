#!/usr/bin/env python
# -*- coding: utf-8 -*-

import itertools as itt
import logging
import numpy as np

from mestrado import pathManipulation as pm
from mestrado import plotModels as pltm
from mestrado.chbmit import utils


def plotCHBMITSignal(raw, file_pattern, ext_args=None):
    """Sript para plotagem do sinal completo presente em *raw*.

    Parâmetros:
    -----------
    raw: mne.Raw
        objeto Raw da bibplioteca mne, contendo informações sobre o sinal.
    file_patter: str
        padrão para salvar o arquivo gerado. Como será gerado apenas um
        arquivo, este padrão não deve conter campos para formatação.
    ext_args: Não é utilizado (default: None)
        este parâmetro é definido para que possa ser chamado dentro da função
        *defaultScript*, do módulo *utils*. Portanto, não é utilizado.
    """
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
        events = [pltm.createEvent('Seizure', estart, eend, 'red')]

    logging.debug(("Definindo função de formatação dos rótulos dos traços nos "
                   "eixos x e y."))

    def y_fmt(x, y):
        return "{}$\mu$V".format(int(x*1e6))

    def x_fmt(x, y):
        return "{:.2f}".format(x/(raw.info['sfreq']*60))

    edf_label = pm.extractFileLabel(file_pattern)
    logging.debug("Gerando plot para {}.".format(edf_label))
    title = "Signal {}".format(edf_label)
    ylabels = raw.ch_names
    ylabels.append('AVG')
    xlabel = 'Time [minutes]'

    pltm.plotChannels(channel_list, signal_len=channel_len, events=events,
                      sharey=True, xformatter=x_fmt, yformatter=y_fmt, dpi=600,
                      title=title, xlabel=xlabel, ylabel=ylabels, xtick_size=2,
                      ytick_size=2, save_path=file_pattern, linewidth=0.1,
                      borderwidth=0.2)

    logging.debug("Finalizando plotagem: {}".format(file_pattern))


def plotCHBMITWindowedSignals(raw, file_pattern, wsize, ext_args=None):
    """Script de plotagem dos sinais em janelas.

    Parâmetros:
    -----------
    raw: mne.Raw
        objeto *Raw*, da biblioteca *mne*, contendo as informações do sinal.
    file_pattern: str
        string contendo o padrão para salvar os arquivos gerados.
    wsize: int
        tamanho da janela utilizada para plotar os sinais (em amostras).
    ext_args: não é utilizado (default: None)
        parâmetro utilizado para a função seja compatível com *defaultScript*.
    """
    # define os índices das janelas
    signal_len = len(raw)
    ws_index = range(0, signal_len, wsize)
    wf_index = range(wsize, signal_len+1, wsize)

    # índices caso as janelas não compreendam todo o sinal
    if wf_index[-1] < signal_len:
        ws_index.append(wf_index[-1])
        wf_index.append(signal_len)

    # gerando evento
    events = None
    if raw.annotations:
        annot = raw.annotations
        elabel = annot.description[0]
        estart = annot.onset*raw.info['sfreq']
        eend = annot.duration*raw.info['sfreq'] + estart
        events = [pltm.createEvent('Seizure', estart, eend, 'red')]

    # cálculo dos dados para plotagem
    data = raw._data
    avg = np.mean(data, axis=0)

    for ws, wf in zip(ws_index, wf_index):
        logging.info("Executando janela: {} -- {}".format(ws, wf))
        # pega apenas os valores dentro da janela
        window = itt.chain(data[:, ws:wf], [avg[ws:wf]])
        window_size = len(data) + 1

        wevents = []
        for ev in events or []:
            wev = pltm.getEventAtWindow(ev, ws, wf)
            if wev:
                wevents.append(wev)

        logging.debug(("Definindo função de formatação dos rótulos dos traços "
                       "nos eixos x e y."))

        def y_fmt(x, y):
            return "{}$\mu$V".format(int(x*1e6))

        def x_fmt(x, y):
            return "{:.2f}".format(x/(raw.info['sfreq']*60))

        # TODO: melhorar isso aqui ----v
        save_path = file_pattern.format(int(float(x_fmt(wsize, 0))),
                                        int(float(x_fmt(ws, 0))),
                                        int(float(x_fmt(wf, 0))))
        flabel = pm.extractFileLabel(save_path)
        logging.info("Gerando plot para {}.".format(flabel))
        title = "Signal {}".format(flabel)

        ylabels = raw.ch_names
        ylabels.append('AVG')
        xlabel = 'Time [minutes]'
        signal_time = range(ws, wf)

        pltm.plotChannels(window, window_size, events=wevents, linewidth=0.1,
                          signal_time=signal_time, sharey=True, title=title,
                          ylabel=ylabels, xlabel=xlabel, xformatter=x_fmt,
                          yformatter=y_fmt, xtick_size=2, ytick_size=2,
                          dpi=600, borderwidth=0.2, save_path=save_path)


def plotCHBMITSizures(raw, file_pattern, fargs, ext_args=None):
    pass


if __name__ == "__main__":
    from mestrado import argline
    from mestrado.chbmit import utils
    # pattern: {}_T{}.png
    # pattern: {}_S{}.png

    argline.config()

    plabel = 'chb01'
    edf_label = '{}_03'.format(plabel)

    edf_path = ('/home/mello/Biblioteca/datasets/chbmit/{}/{}.edf'
                ''.format(plabel, edf_label))
    sum_path = ('/home/mello/Biblioteca/datasets/chbmit/{}/{}-summary.txt'
                ''.format(plabel, plabel))

    annot_dict = utils.summaryFileParser(sum_path)
    raw = utils.openEDF(edf_path, annot_dict)

    fpattern = '{}_T{}-{}.png'.format(edf_label, '{}', '{}')
    wsize = int(10*60*raw.info['sfreq'])     # 10 minutos

    plotCHBMITWindowedSignals(raw, fpattern, wsize, edf_label=edf_label)
