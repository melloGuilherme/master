#!/usr/bin/env python
# -*- coding: utf-8 -*-

import collections
import logging
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable


def createEvent(label, start, end, color):
    """Retorna um evento para ser plotado na barra de eventos.

    Parâmetros:
    -----------
    label: str
        rótulo do evento.
    start: list
        lista contendo o tempo inicial dos eventos.
    end: list
        lista contendo o tempo final dos eventos.
    color: (float, float, float) ou str
        cor em que os eventos serão plotados. Podem ser tupla com os valores
        RGB ou string com uma cor válida.
    """
    Event = collections.namedtuple('Event', ['label','start','end','color'])
    e = Event(label, start, end, color)
    return e


def configEventBar(ax, events, pad):
    """Configura uma nova barra (eixo) e plota marcações de eventos.

    Parâmetros:
    -----------
    ax: Axes
        eixo ao qual serão inseridos eventos.
    events: list de Event
        lista de eventos a serem plotados. Events são criados por meio do
        método *createEvent*.
    pad: float
        distância entre o eixo e a barra de eventos.
    """
    divider = make_axes_locatable(ax)
    height = 0.08 * len(events)
    event_bar = divider.append_axes('bottom', height, pad=pad, sharex=ax)

    plt.setp(ax.get_xticklabels(), visible=False)

    plt.setp(event_bar.get_xticklabels(), visible=True, fontsize='x-small')
    plt.setp(event_bar.get_yticklabels(), visible=True, fontsize=6)
    plt.setp(event_bar.get_yticklines(), visible=False)

    event_bar.spines['top'].set_visible(False)
    event_bar.spines['left'].set_visible(False)
    event_bar.spines['right'].set_visible(False)

    event_bar.xaxis.set_ticks_position('bottom')

    bar_labels = []
    for idx, ev in enumerate(events):
        for occ in zip(ev.start, ev.end):
            start = occ[0]
            end = occ[1]
            duration = end-start
            event_bar.barh(idx, duration, height=1, left=start, alpha=0.65,
                           facecolor=ev.color, edgecolor=ev.color)

        bar_labels.append(ev.label)

    event_bar.set_yticks([i+0.5 for i in range(len(bar_labels))])
    event_bar.set_yticklabels(bar_labels)


def defaultPlotStruct(subplot_size, title=None, figsize=None,
                      subplot_space=0.03, borderwidth=1, xlabel=None,
                      xticklabel_positions=None, xticklabel_values=None,
                      xtickline_visible=True, xticklabel_visible=True,
                      xtick_bins=None, xtick_size=None, ylabel=None,
                      yticklabel_positions=None, yticklabel_values=None,
                      ytickline_visible=True, yticklabel_visible=True,
                      ytick_bins=None, ytick_size=None, events=None):
    """Cria uma estrutura de plotagem retornando uma *plt.Figure* e *plt.Axes*

    Fução responsável por construir a estrutura básica de plotagem, com vários
    subplots compartilhando o eixo x (uma coluna). Apenas a estrutura é gerada
    e configurada de acordo com os parâmetros recebidos. Nenhuma plotagem é de
    fato realizada, a qual deve ser implementada, chamando esta função. Esta
    estrutura é útil para gerar uma imagem/plot de várias séries temporais que
    compartilham o eixo x, e.i., canais de EEG, coeficientes das transformadas
    (Fourier/Wavelet), espectro de potência para STFT.

    Parâmetros:
    -----------
    subplot_size: int
        número de subplots a serem criados (número de linhas).
    title: str (default: None)
        string para o título. Posicionado na parte superior da imagem.
    figsize: (int, int) (default: None)
        largura e altura da imagem, em polegadas (inches).
    subplot_space: float (default: 0.03)
        espaçamento vertical entre eixos (subplots).
    borderwidth: float (default: 1)
        define a largura das bordas (eixos) e marcações (ticks), em pontos.
    xlabel: str (default: None)
        string contendo o rótulo do eixo x, posicionado abaixo da última linha.
    xticklabel_positions: list de int (default: None)
        lista contendo a posição das marcações (ticks) do eixo x. Deve ser
        usado em conjunto com *xticklabel_values*, ou não terá efeitos.
    xticklabel_values: list (default: None)
        lista contendo os rótulos correspondentes as marcações (ticks). Deve
        ser usado em conjunto com *xticklabel_positions*, ou não terá efeitos.
    xtickline_visible: True|False (default: True)
        booleano que define a visibilidade das marcações no eixo x (tick).
    xticklabel_visible: True|False (default: True)
        booleano que define a visibilidade dos rótulos dos traços no eixo x.
    xtick_bins: int (default: None)
        define o número de bins no eixo x.
    xtick_size: float (default: None)
        define o tamanho dos ticks do eixo x, em pontos.
    ylabel: str (default: None)
        string contendo o rótulo do eixo y.
    yticklabel_positions: list de int (default: None)
        lista contendo a posição das marcações (ticks) do eixo y.
    yticklabel_values: list (default: None)
        lista contendo os rótulos correspondentes as marcações (ticks).
    ytickline_visible: True|False (default: True)
        booleano que define a visibilidade das marcações no eixo y (tick).
    yticklabel_visible: True|False (default: True)
        booleano que define a visibilidade dos rótulos dos traços no eixo y.
    ytick_bins: int (default: None)
        define o número de bins no eixo y.
    ytick_size: float (default: None)
        define o tamanho dos ticks do eixo y, em pontos.
    events: list de Event (default: None)
        lista contendo instâncias da classe Event com informações sobre eventos
        a serem marcados. Os eventos podem ser criados por meio do método
        *createEvent*.
"""
    logging.debug(("Criando estrutura de plotagem com "
                   "{} áreas.".format(subplot_size)))

    fig, axes = plt.subplots(subplot_size, sharex=True, figsize=figsize)

    # caso exista apenas 1 subplot, axes não será iterável
    if not isinstance(axes, collections.Iterable):
        logging.debug("Tornando eixos iteráveis.")
        axes = [axes]

    logging.debug("Iniciando configurações comuns aos eixos.")
    for index, ax in enumerate(axes):
        if ylabel is not None:
            logging.debug("Definindo rótulo do eixo({}) y.".format(index))
            ax.set_ylabel(ylabel[index].decode('utf-8'), fontsize='x-small',
                          rotation=0, ha='right')

        # define a visibilidade dos valores do eixo y
        plt.setp(ax.get_yticklines(), visible=ytickline_visible)
        plt.setp(ax.get_yticklabels(), visible=yticklabel_visible, fontsize=4)

        plt.setp(ax.get_xticklines(), visible=xtickline_visible)

        ax.ticklabel_format(style='plain', axis='both')

        for ax_pos in ['top', 'bottom', 'left', 'right']:
            ax.spines[ax_pos].set_linewidth(borderwidth)

        if xtick_size is not None:
            ax.tick_params(axis='x', length=xtick_size)

        if ytick_size is not None:
            ax.tick_params(axis='y', size=ytick_size)

        ax.tick_params(axis='both', width=borderwidth)

        if ytick_bins is not None:
            logging.debug("Defindo o número de bins no eixo y.")
            ax.locator_params(axis='y', nbins=ytick_bins)
        else:
            if yticklabel_values is not None:
                logging.debug(("Definindo valores para as marcações do eixo "
                               "({}) y.".format(index)))
                ax.set_yticklabels(yticklabel_values)

            if yticklabel_positions is not None:
                logging.debug(("Definindo posições para as marcações do eixo "
                               "({}) y.".format(index)))
                ax.set_yticks(yticklabel_positions)

    logging.debug("Iniciando configurações gerais.")

    logging.debug("Definindo configurações das marcações do eixo x.")
    if xtick_bins is not None:
        logging.debug("Defindo o número de bins no eixo x.")
        ax.locator_params(axis='x', nbins=xtick_bins)
    elif xticklabel_values is not None and xticklabel_positions is not None:
        # TODO: esta parte está causando erro no plot. Está configurando apenas
        #       no último plot, enquanto some com as marcações dos outros
        logging.debug("Definindo posições e valores das marcações no eixo x.")
        plt.xticks(xticklabel_positions, xticklabel_values)

    plt.setp(axes[-1].get_xticklabels(), fontsize='xx-small',
             visible=xticklabel_visible)

    if xlabel is not None:
        logging.debug("Definindo rótulo do eixo x.")
        axes[-1].set_xlabel(xlabel.decode('utf-8'), fontsize='x-small')

    # configurando barra de eventos
    if events is not None:
        configEventBar(axes[-1], events, subplot_space)

    # melhora o espaçamento do plot
    plt.tight_layout()

    # ajusta o espaçamento entre subplots
    plt.subplots_adjust(hspace=subplot_space)

    if title is not None:
        logging.debug("Definindo o título da imagem: {}".format(title))
        plt.subplots_adjust(top=0.95)
        plt.suptitle(title.decode('utf-8'), fontsize='medium', visible=True)

    return fig, axes


def plotChannels(signals, signals_len=None, signal_time=None, save_path=None,
                 dpi=150, linewidth=1, **kwargs):
    """Faz a plotagem de séries temporais em subplotes separados.

    Função responsável pela plotagem de séries temporais de uma dimensão, como:
    transformadas de Fourier e outras medidas que variam de acordo com alguma
    variável (tempo,frequência,etc.). O plot pode ser configurado de diferentes
    formas.

    Parâmetros:
    -----------
    signals: array_like|iterador
        Se for um array_like, deve conter 2 dimensões. Se for um iterador, cada
        elemento deve conter um vetor para plotagem. Caso seja utilizado um
        iterador, é necessário passar a quantidade de sinais por meio do
        parâmetro 'signals_len'.
    signals_len: int (default: None)
        necessário quando é utilizado um iterador no parâmetro *signals*,
        representa a quantidade de sinais que serão plotados.
    signal_time: array_like (default: None)
        valores da coordenada x, correspondem às ocorrencias do sinal (tempo,
        frequência). Caso None, será utilizado o número da ocorrência
        (sequência de números inteiros).
    save_path: str|None (default: None)
        caminho para salvar a imagem gerada. Caso não seja passado (None), será
        plotado na tela com *plt.show()*.
    dpi: float (default:150)
        resolução da imagem em dpi (pontos por polegada).
    linewidth: float (default: 1)
        largura da linha plotada (em pontos)
    **kwargs:
        as palavras chave restantes são propriedades da função
        *defaultPlotStruct*. Ver *defaultPlotStruct* para mais detalhes.
"""
    if isinstance(signals, collections.Iterator) and signal_len is None:
        errormsg = ("Para o parâmetro 'signals' ({}) é necessário passar o "
                    "tamanho utilizando o parâmetro 'signals_len' ({})"
                    "".format(type(signals), signals_len))
        logging.error(errormsg)
        raise ValueError(errormsg)
    else:
        signals_len = len(signals)

    logging.debug("Criando estrutura de eixos de plotagem.")
    fig, axes = defaultPlotStruct(signals_len, **kwargs)

    if signal_time is None:
        signal_time = range(len(signals[0]))

    for index, (s, ax) in enumerate(zip(signals, axes)):
        logging.debug("Plotando sobre eixo {}.".format(index))
        ax.plot(signal_time, s, linewidth=linewidth)

    if save_path is None:
        logging.debug("Exibindo imagem na tela.")
        plt.show()
    else:
        logging.debug("Salvando imagem em: {}".format(save_path))
        plt.savefig(save_path, dpi=dpi)
        plt.close()
    logging.debug("Finalizando plotagem.")


def plotSpectrum(signals, signals_len=None, extent=None, save_path=None,
                 dpi=150, **kwargs):
    """Faz a plotagem de uma imagem, na forma de mapa de cores.

    Função responsável pela plotagem dos espectros de potência com duas
    dimensões (STFT), em que as colunas representam as janelas, e as linhas as
    componentes de frequências.

    Parâmetros:
    -----------
    signals: array_like|iterador
        Se for um array_like, deve conter 3 dimensões. Se for um iterador, cada
        elemento deve conter 2 dimensões para plotagem. Caso seja utilizado um
        iterador, é necessário passar a quantidade de sinais/espectros por meio
        do parâmetro *signals_len*.
    signals_len: int (default: None)
        necessário quando é utilizado um iterador no parâmetro *signals*,
        representa a quantidade de sinais que serão plotados.
    extent: [int, int, int, int] (default: None)
        vetor com quatro posições [minX, maxX, minY, maxY], representando os
        valores máximos e mínimos para os eixos X e Y dos subplots.
    save_path: str (default:None)
        caminho para salvar a imagem gerada. Caso não seja passado (None), será
        plotado na tela com *plt.show()*.
    dpi: float (default:150)
        resolução da imagem em dpi (pontos por polegada).
    **kwargs:
        as palavras chave restantes são propriedades da função
        *defaultPlotStruct*. Ver *defaultPlotStruct* para mais detalhes.
"""
    if isinstance(signals, collections.Iterator) and signal_len is None:
        errormsg = ("Para o parâmetro 'signals' ({}) é necessário passar o "
                    "tamanho utilizando o parâmetro 'signals_len' ({})"
                    "".format(type(signals), signals_len))
        logging.error(errormsg)
        raise ValueError(errormsg)
    else:
        signals_len = len(signals)

    logging.debug("Criando estrutura de eixos de plotagem.")
    fig, axes = defaultPlotStruct(signals_len, **kwargs)

    # TODO: axes.flat dá erro quando tem apenas 1 eixo de plotagem
    for index, (s, ax) in enumerate(zip(signals, axes.flat)):
        logging.debug("Plotando sobre eixo {}.".format(index))
        im = ax.imshow(s, origin='lower', aspect='auto', extent=extent)
        cbar = fig.colorbar(im, ax=ax, pad=0.02)
        cbar.ax.tick_params(labelsize='xx-small')

    if save_path is None:
        logging.debug("Exibindo imagem na tela.")
        plt.show()
    else:
        logging.debug("Salvando imagem em: {}".format(save_path))
        plt.savefig(save_path, dpi=dpi)
        plt.close()
    logging.debug("Finalizando plotagem.")
