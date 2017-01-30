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

    logging.debug("Criando lista (iterador) com canais e média.")
    channel_list = itt.chain(raw._data)
    channel_len = len(raw._data)

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

    edf_label = pm.extractFileLabel(file_pattern)
    logging.debug("Gerando plot para {}.".format(edf_label))
    title = "Signal {}".format(edf_label)
    ylabels = raw.ch_names
    xlabel = 'Time [Hours]'

    def y_fmt(x, y):
        return "{}$\mu$V".format(int(x*1e6))

    def x_fmt(x, y):
        s, r = divmod(x, raw.info['sfreq'])     # segundos
        ms = r/float(raw.info['sfreq'])         # milissegundos
        m, s = divmod(int(s), 60)               # minutos
        h, m = divmod(m, 60)                    # hora
        return "{:02d}:{:02d}:{:02.3f}".format(h, m, (s+ms))

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
            s, r = divmod(x, raw.info['sfreq'])     # segundos
            ms = r/float(raw.info['sfreq'])         # milissegundos
            m, s = divmod(int(s), 60)               # minutos
            h, m = divmod(m, 60)                    # hora
            return "{:02d}:{:02d}:{:02.3f}".format(h, m, (s+ms))

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


def plotCHBMITSizures(raw, file_pattern, ext_args=None):
    """Plotagem das crises presentes no sinal, se existirem.

    Recebe informações sobre um sinal e plota os momentos de crise presentes no
    sinal, se existirem.

    Parâmetros:
    -----------
    raw: mne.Raw
        objeto *Raw* contendo informações sobre o sinal.
    file_pattern: str
        string contendo o padrão para salvar os arquivos gerados por este
        script. Se necessário, deve conter campos para formatação.
    ext_args: não é usado (default: None)
        parâmetro utilizado para que esta função seja compatível com
        *defaultScript*.
    """
    if not raw.annotations:
        logging.info(("Arquivo não contém anotações de crises. "
                      "Não será executado."))
        return

    logging.info("Executando plotagem das crises de epilepsia.")
    annot = raw.annotations
    elabel = annot.description[0]
    estart = annot.onset*raw.info['sfreq']
    eend = annot.duration*raw.info['sfreq'] + estart

    data = raw._data
    avg = np.mean(data, axis=0)
    for idx, (start, end) in enumerate(zip(estart, eend)):
        # selecionando até 30s antes da crise
        ws = start - raw.info['sfreq']*60
        ws = int(ws) if ws > 0 else 0

        # selecionando até 30s depois da crise
        wf = end + raw.info['sfreq']*60
        wf = int(wf) if wf < len(raw) else len(raw)

        # extrai a janela para plotagem
        window = data[:, ws:wf]
        wavg = avg[ws:wf]

        # cria iterado para plotagem
        signals = itt.chain(window, [wavg])
        signals_len = len(window) + 1

        # cria um evento contendo apenas uma crise
        event = pltm.createEvent(elabel, [start], [end], 'red')

        # parâmetros de configuração do plot
        sd = (end-start)/raw.info['sfreq']  # duração da crise, em segundos
        title = file_pattern.format(idx, '{}s'.format(sd))
        title = pm.extractFileLabel(title)
        xlabel = "Time"
        ylabels = raw.ch_names
        ylabels.append('AVG')
        signal_time = range(ws, wf)
        save_path = file_pattern.format(idx, '{}s'.format(sd))

        def y_fmt(x, y):
            return "{}$\mu$V".format(int(x*1e6))

        def x_fmt(x, y):
            s, r = divmod(x, raw.info['sfreq'])     # segundos
            ms = r/float(raw.info['sfreq'])         # milissegundos
            m, s = divmod(int(s), 60)               # minutos
            h, m = divmod(m, 60)                    # hora
            return "{:02d}:{:02d}:{:02.3f}".format(h, m, (s+ms))

        # plotagem do sinal selecionado
        pltm.plotChannels(signals, signals_len, sharey=True, xlabel=xlabel,
                          ylabel=ylabels, title=title, xformatter=x_fmt,
                          yformatter=y_fmt, events=[event],
                          signal_time=signal_time, ytick_bins=4,
                          linewidth=0.2, xtick_size=2, ytick_size=2,
                          dpi=600, borderwidth=0.2, save_path=save_path)


def plotCHBMITSignalStatistic(raw, fpattern, wsize, hop, ext_args=None):
    """Plotagem da evolução da média e do desvio padrão utilizando janelas.

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
    # define os índices de limites das janelas
    signal_len = len(raw)
    ws_index = range(0, signal_len-wsize+1, hop)
    wf_index = range(wsize, signal_len+1, hop)

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

    # vetores para armazenar os resultados
    mean = [[] for i in range(len(data)+1)]
    std = [[] for i in range(len(data)+1)]
    windex = []

    # cálculo da média e desvio padrão usando janelas deslizantes
    for ws, wf in zip(ws_index, wf_index):
        wi = int((ws+wf)/2)
        logging.debug("Executando janela({}) {} -- {}".format(wi, ws, wf))

        windex.append(wi)

        # pega apenas os valores dentro da janela
        window = np.append(data[:, ws:wf], [avg[ws:wf]], axis=0)

        # cálculo da média e desvio padrão da janela
        wmean = np.mean(window, axis=1)
        wstd = np.std(window, axis=1)

        for i, (m, s) in enumerate(zip(wmean, wstd)):
            mean[i].append(m)
            std[i].append(s)

    mean = np.array(mean)
    std = np.array(std)

    logging.debug(("Definindo função de formatação dos rótulos dos traços "
                   "nos eixos x e y."))

    def y_fmt(x, y):
        return "{}$\mu$V".format(int(x*1e6))

    def x_fmt(x, y):
        s, r = divmod(x, raw.info['sfreq'])     # segundos
        ms = r/float(raw.info['sfreq'])         # milissegundos
        m, s = divmod(int(s), 60)               # minutos
        h, m = divmod(m, 60)                    # hora
        return "{:02d}:{:02d}:{:02.3f}".format(h, m, (s+ms))

    save_path = fpattern.format(wsize, hop)
    flabel = pm.extractFileLabel(save_path)
    logging.info("Gerando plot para {}.".format(flabel))
    title = "Signal Mean and Standard Deviation: {}".format(flabel)

    ylabels = raw.ch_names
    ylabels.append('AVG')
    xlabel = 'Time'

    pltm.plotErrorSignal(mean, std, std*(-1), sharey=True, linewidth=0.1,
                         events=events, title=title, ylabel=ylabels,
                         xlabel=xlabel, xformatter=x_fmt, signal_time=windex,
                         yformatter=y_fmt, xtick_size=2, ytick_size=2,
                         dpi=600, borderwidth=0.2, save_path=save_path)
