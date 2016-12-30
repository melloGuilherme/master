#!/usr/bin/env python
# -*- coding: utf-8 -*-

import collections
import logging
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import ticker
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
    Event = collections.namedtuple('Event', ['label', 'start', 'end', 'color'])
    e = Event(label, start, end, color)
    return e


def getEventAtWindow(event, wsi, wfi):
    """Retorna um objeto *Event*, com informações correspondentes a uma janela.

    Recebe um objeto *Event* e os valores de início e fim da janela de tempo de
    interesse. Extrai as informações deste evento contidas no intervalo de
    tempo desejado, retornando um novo objeto *Event*. Caso não existam
    informações sobre o evento dentro do intervalo desejado, será retornado
    None. Utilizando a notação de intervalos, o conteúdo da janela é dado por
    [wsi,wfi).

    Parâmetros:
    -----------
    event: Event
        Objeto do tipo *Event*.
    wsi: int
        índice do limite inferior da janela (em amostras).
    wfi: int
        índice do limite superior da janela (em amostras). Este valor não está
        incluso na janela, ou seja, [wsi,wfi)

    Retorno:
    --------
    Event ou None:
        caso existam informações dentro do intervalo de tempo desejado, será
        retornado um *Event*, caso contrário, será retornado None.
    """
    s = []  # tempos de início dos eventos
    f = []  # tempos de término dos eventos
    for start, end in zip(event.start, event.end):
        # caso 1: o evento começa na janela
        if start > wsi and start < wfi:
            s.append(start)
            if end < wfi:
                f.append(end)
            else:
                f.append(wfi)
        # caso 2: o evento ocorre por toda a janela
        elif start < wsi and end > wfi:
            s.append(wsi)
            f.append(wfi)
        # caso 3: o evento termina na janela. OBS.: Se entrar aqui, o evento
        # sempre começará em uma janela anterior, pois se começar nesta janela,
        # entrará no caso 1.
        elif end > wsi and end < wfi:
            s.append(wsi)
            f.append(end)

    if len(f) != len(s):
        msg = "Erro ao criar evento para uma janela."
        logging.error(msg)
        raise ValueError
    elif len(f) == 0 and len(s) == 0:
        wevent = None
    else:
        wevent = createEvent(event.label, s, f, event.color)

    return wevent


def configEventBar(fig, ax, events_len, pad=0.01, bottom=0.06):
    """Configura uma nova barra (eixo) e para plota marcações de eventos.

    Parâmetros:
    -----------
    fig: Figure
        figura gerada pela biblioteca Matplotlib.
    ax: Axes
        eixo ao qual serão inseridos eventos.
    events_len: int
        número de eventos a serem plotados. Events são criados por meio do
        método *createEvent*.
    pad: float (default: 0.01)
        distância entre o eixo e a barra de eventos (em proporção, normalizada
        para 1)
    bottom: float (default: 0.06)
        distância até a parte inferior da barra de eventos (em proporção,
        normalizada para 1)

    Retorno:
    --------
    matplotlib.Axes:
        retorna uma instância de eixos, referente ao eixo da barra de eventos.
    """
    # pega a posição da última área de plotage
    bbox = ax.get_position()

    # extrai as posições para a barra de eventos
    left = bbox.x0
    height = 0.01 * events_len
    width = bbox.width

    # cria a barra de eventos, já posicionada
    rect = [left, bottom, width, height]
    event_bar = fig.add_axes(rect)

    # ajusta as áreas de plotagem para
    # que caiba a barra de eventos
    vspace = bottom+height+pad
    fig.subplots_adjust(bottom=vspace)

    # configurações do eixo
    plt.setp(ax.get_xticklabels(), visible=False)

    # xonfigurações da barra de eventos
    plt.setp(event_bar.get_xticklabels(), visible=True, fontsize='xx-small')
    plt.setp(event_bar.get_yticklabels(), visible=True, fontsize=6)
    plt.setp(event_bar.get_yticklines(), visible=False)

    event_bar.spines['top'].set_visible(False)
    event_bar.spines['left'].set_visible(False)
    event_bar.spines['right'].set_visible(False)

    event_bar.xaxis.set_ticks_position('bottom')

    return event_bar


def plotEventBar(ebar, events, xlim=None):
    """Plota eventos em uma barra de eventos já configurada.

    Parâmetros:
    -----------
    ebar: Axes
        barra de plotagem (Axes) já configurada. Gerada a partir do método
        *configEventBar*.
    events: list de Event
        lista contendo os eventos a serem plotados.
    xlim: (int, int) (default: None)
        tupla, ou lista, de dois elementos. Correspondendo aos valores mínimo
        e máximo que definem um intervalo para o eixo x.
    """
    bar_labels = []

    # percorre eventos
    for idx, ev in enumerate(events):
        # percorre ocorrências. Um evento pode ter mais de uma ocorrência para
        # ser marcada em um único sinal.
        for occ in zip(ev.start, ev.end):
            start = occ[0]
            end = occ[1]
            duration = end-start
            # plotagem de uma barra horizontal
            ebar.barh(idx, duration, height=1, left=start, alpha=0.65,
                      facecolor=ev.color, edgecolor=ev.color)

        bar_labels.append(ev.label)

    # configurações de plotagem dos rótulos do eixo y
    ebar.set_yticks([i+0.5 for i in range(len(bar_labels))])
    ebar.set_yticklabels(bar_labels)

    if xlim:
        ebar.set_xlim(xlim)


def defaultPlotStruct(subplot_size, title=None, figsize=None, sharey=False,
                      subplot_space=0.03, borderwidth=1, xlabel=None,
                      xticklabel_positions=None, xticklabel_values=None,
                      xtickline_visible=True, xticklabel_visible=True,
                      xtick_bins=None, xtick_size=None, ylabel=None,
                      yticklabel_positions=None, yticklabel_values=None,
                      ytickline_visible=True, yticklabel_visible=True,
                      ytick_bins=None, ytick_size=None, yformatter=None,
                      events_len=None, xformatter=None):
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
    sharey: True|False (default: False)
        define o compartilhamento do eixo y entre *subplots*.
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
    yformatter: funtion (default: None)
        função para formatação dos rótulos no eixo y utilizando FuncFormatter.
        Esta função deve conter dois parâmetros (referentes à posição e rótulo
        de um *tick*) e retornar apenas um valor, o qual será utilizado para
        definir o rótulo do *tick*.
    events: list de Event (default: None)
        lista contendo instâncias da classe Event com informações sobre eventos
        a serem marcados. Os eventos podem ser criados por meio do método
        *createEvent*.
    xformatter: function (default: None)
        função para formatação dos rótulos no eixo x utilizando FuncFormatter.
        Esta função deve conter dois parâmetros (referentes à posição e rótulo
        de um *tick*) e retornar apenas um valor, o qual será utilizado para
        definir o rótulo do *tick*.
"""
    logging.debug(("Criando estrutura de plotagem com "
                   "{} áreas.".format(subplot_size)))

    fig, axes = plt.subplots(subplot_size, sharex=True, sharey=sharey,
                             figsize=figsize)

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

        for ax_pos in ['top', 'bottom', 'left', 'right']:
            ax.spines[ax_pos].set_linewidth(borderwidth)

        if xtick_size is not None:
            ax.tick_params(axis='x', length=xtick_size)

        if ytick_size is not None:
            ax.tick_params(axis='y', size=ytick_size)

        ax.tick_params(axis='both', width=borderwidth)

        if yformatter:
            yfmt = ticker.FuncFormatter(yformatter)
            ax.yaxis.set_major_formatter(yfmt)

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
    ax = axes[-1]

    # melhora o espaçamento do plot
    plt.tight_layout()

    # ajusta o espaçamento entre subplots
    plt.subplots_adjust(hspace=subplot_space)

    if title is not None:
        logging.debug("Definindo o título da imagem: {}".format(title))
        plt.subplots_adjust(top=0.95)
        plt.suptitle(title.decode('utf-8'), fontsize='medium', visible=True)

    # configurando barra de eventos
    event_bar = None
    if events_len is not None and events_len > 0:
        event_bar = ax = configEventBar(fig, ax, events_len)
        plt.setp(ax.get_xticklines(), visible=xtickline_visible)
        ax.spines['bottom'].set_linewidth(borderwidth)
        if xtick_size is not None:
            ax.tick_params(axis='x', length=xtick_size)
        ax.tick_params(axis='both', width=borderwidth)

    if xformatter:
        xfmt = ticker.FuncFormatter(xformatter)
        ax.xaxis.set_major_formatter(xfmt)

    if xlabel is not None:
        logging.debug("Definindo rótulo do eixo x.")
        ax.set_xlabel(xlabel.decode('utf-8'), fontsize='x-small')

    logging.debug("Definindo configurações das marcações do eixo x.")
    if xtick_bins is not None:
        logging.debug("Defindo o número de bins no eixo x.")
        ax.locator_params(axis='x', nbins=xtick_bins)
    elif xticklabel_values is not None and xticklabel_positions is not None:
        # TODO: esta parte está causando erro no plot. Está configurando apenas
        #       no último plot, enquanto some com as marcações dos outros
        logging.debug("Definindo posições e valores das marcações no eixo x.")
        plt.xticks(xticklabel_positions, xticklabel_values)

    plt.setp(ax.get_xticklabels(), fontsize='xx-small',
             visible=xticklabel_visible)

    return fig, axes, event_bar


def plotChannels(signals, signal_len=None, signal_time=None, save_path=None,
                 dpi=150, linewidth=1, events=None, **kwargs):
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
    signal_len: int (default: None)
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
    events: list de Event (default: None)
        lista de eventos a serem plotados na barra de eventos.
    **kwargs:
        as palavras chave restantes são propriedades da função
        *defaultPlotStruct*. Ver *defaultPlotStruct* para mais detalhes.
"""
    if isinstance(signals, collections.Iterator):
        if signal_len is None:
            errormsg = ("Para o parâmetro 'signals' ({}) é necessário passar "
                        "o tamanho utilizando o parâmetro 'signal_len' ({})"
                        "".format(type(signals), signal_len))
            logging.error(errormsg)
            raise ValueError(errormsg)
    else:
        signal_len = len(signals)

    logging.debug("Criando estrutura de eixos de plotagem.")
    events_len = 0 if events is None else len(events)
    fig, axes, event_bar = defaultPlotStruct(signal_len, events_len=events_len,
                                             **kwargs)

    for index, (s, ax) in enumerate(zip(signals, axes)):
        logging.debug("Plotando sobre eixo {}.".format(index))
        if signal_time is None:
            ax.plot(s, linewidth=linewidth)
        else:
            ax.plot(signal_time, s, linewidth=linewidth)

    if event_bar and events:
        xlim = axes[-1].get_xlim()
        plotEventBar(event_bar, events, xlim)

    if save_path is None:
        logging.debug("Exibindo imagem na tela.")
        plt.show()
    else:
        logging.debug("Salvando imagem em: {}".format(save_path))
        plt.savefig(save_path, dpi=dpi)
        plt.close()
    logging.debug("Finalizando plotagem.")


def plotSpectrum(signals, xvalues, yvalues, signals_len=None, save_path=None,
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
    xvalues: array_like
        vetor com valores do eixo x (componente de tempo da STFT).
    yvalues: array_like
        vetor com valores do eixo y (componentes de frequência da STFT).
    signals_len: int (default: None)
        necessário quando é utilizado um iterador no parâmetro *signals*,
        representa a quantidade de sinais que serão plotados.
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
        from matplotlib import colors
        im = ax.pcolormesh(xvalues, yvalues, s, cmap='RdBu_r',
                           norm=colors.PowerNorm(gamma=0.5))
        ax.axis('tight')
        cbar = fig.colorbar(im, ax=ax, pad=0.01)
        cbar.ax.tick_params(labelsize=5)

    if save_path is None:
        logging.debug("Exibindo imagem na tela.")
        plt.show()
    else:
        logging.debug("Salvando imagem em: {}".format(save_path))
        plt.savefig(save_path, dpi=dpi)
        plt.close()
    logging.debug("Finalizando plotagem.")


def plotErrorSignal(signals, top_err, bottom_err, signals_len=None, dpi=150,
                    signal_time=None, save_path=None, linewidth=1, events=None,
                    **kwargs):
    """Faz a plotagem de séries temporais, mostrando um intervalo de erro.

    Função responsável pela plotagem de séries temporais de uma dimensão,
    mostrando um intervalo de erro. Este erro pode ser considerado o desvio
    padrão (ou a variância), ao plotar uma média ou o sinal.

    Parâmetros:
    -----------
    signals: array_like|iterador
        Se for um array_like, deve conter 2 dimensões. Se for um iterador, cada
        elemento deve conter um vetor para plotagem. Caso seja utilizado um
        iterador, é necessário passar a quantidade de sinais por meio do
        parâmetro 'signals_len'.
    top_err: array_like|iterador
        idem ao *signals*. Deve conter, também, a mesma dimensão que *signals*.
        Para cada elemento em *signals* deve existir um em *top_err*.
    bottom_err: array_like|iterador
        idem ao *signals*, Deve conter, também, a mesma dimensão que *signals*.
        Para cada elemento em *signals* deve existir um em *bottom_err*.
    signals_len: int (default: None)
        necessário quando é utilizado um iterador no parâmetro *signals*,
        representa a quantidade de sinais que serão plotados.
    dpi: float (default:150)
        resolução da imagem em dpi (pontos por polegada).
    signal_time: array_like (default: None)
        valores da coordenada x, correspondem às ocorrencias do sinal (tempo,
        frequência). Caso None, será utilizado o número da ocorrência
        (sequência de números inteiros).
    save_path: str|None (default: None)
        caminho para salvar a imagem gerada. Caso não seja passado (None), será
        plotado na tela com *plt.show()*.
    linewidth: float (default: 1)
        largura da linha plotada (em pontos)
    events: list de Event (default: None)
        lista de eventos a serem plotados na barra de eventos.
    **kwargs:
        as palavras chave restantes são propriedades da função
        *defaultPlotStruct*. Ver *defaultPlotStruct* para mais detalhes.
"""
    if (isinstance(signals, collections.Iterator) and
            isinstance(top_err, collections.Iterator) and
            isinstance(bottom_err, collections.Iterator)):

        if signals_len is None:
            errormsg = ("É necessário passar o tamanho dos sinais utilizando "
                        "o parâmetro 'signals_len' ({})".format(signals_len))
            logging.error(errormsg)
            raise ValueError(errormsg)
    elif (isinstance(signals, (np.ndarray, list)) and
          isinstance(top_err, (np.ndarray, list)) and
          isinstance(bottom_err, (np.ndarray, list))):
        signals_len = len(signals)
    else:
        errormsg = ("Os parâmetros de sinal e de erro devem possuir tipos "
                    "iguais.")
        logging.error(errormsg)
        raise ValueError(errormsg)

    logging.debug("Criando estrutura de eixos de plotagem.")
    events_len = 0 if events is None else len(events)
    fig, axes, event_bar = defaultPlotStruct(signals_len,
                                             events_len=events_len, **kwargs)

    for index, (s, t, b, ax) in enumerate(zip(signals, top_err, bottom_err,
                                              axes)):
        logging.debug("Plotando sobre eixo {}.".format(index))

        if signal_time is None:
            signal_time = range(len(s))

        ax.plot(signal_time, s, color='g', linewidth=linewidth)
        ax.fill_between(signal_time, t, b, alpha=0.35, edgecolor='g',
                        facecolor='y', linewidth=linewidth)

    if event_bar and events:
        xlim = axes[-1].get_xlim()
        plotEventBar(event_bar, events, xlim)

    if save_path is None:
        logging.debug("Exibindo imagem na tela.")
        plt.show()
    else:
        logging.debug("Salvando imagem em: {}".format(save_path))
        plt.savefig(save_path, dpi=dpi)
        plt.close()
    logging.debug("Finalizando plotagem.")
