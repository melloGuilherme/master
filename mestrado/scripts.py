#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

from mestrado import chbmit
from mestrado import argline


def execDatasetFileVerifier():
    """Verifica a integridade das bases de dados.

    Para cada base de dados utilizada, é chamada uma função diferente. Esta
    função faz as chamadas de forma ordenada, mantendo registros de log.

    Nota:
    -----
    Os parâmetros de configuração são passados por linha de comando. Para mais
    informações, ver o módulo *argline*.
    """
    import chbmit.fileVerifier
    argline.config()

    print "Iniciando verificação de arquivos."

    print "Verificando Base: CHBMIT."
    chbmit.fileVerifier.verifyCHBMITFiles()

    print "Verificação Concluída!"


def execSignal():
    """Plotagem dos sinais (inteiros) das bases de dados."""
    import chbmit.signal
    import chbmit.utils

    argline.config()

    print "Iniciando plotagem dos sinais."

    print "Plotando sinais: CHBMIT."
    f = chbmit.signal.plotCHBMITSignal
    fpattern = "{}_signal.png"
    fargs = ()

    save_dir = argline.OUTPUTDIR if argline.OUTPUTDIR else '.'
    chbmit.utils.defaultScript(f, fpattern, fargs=None, patients='good',
                               save_dir=save_dir, exec_mode=None)

    print "Plotagem dos sinais completos concluída."


def execWindowedSignal():
    """Plotagem dos sinais em janelas."""
    import chbmit.signal
    import chbmit.utils

    argline.config()

    f = chbmit.signal.plotCHBMITWindowedSignals
    fpattern = "{}_signal_T{}-{}-{}.png"

    wsize = int(10*60*256)     # 10 minutos
    fargs = [(wsize,)]
    eargs = [('{}',)*3]

    save_dir = argline.OUTPUTDIR if argline.OUTPUTDIR else '.'

    # exec_mode=None é utilizado por não existir suporte para limpeza de
    # arquivos que utilizam argumentos de plotagem (ext_args), como os índices
    # dos limites das janelas plotadas. TODO: inserir suporte
    chbmit.utils.defaultScript(f, fpattern, fargs, patients='good',
                               ext_args=eargs, save_dir=save_dir,
                               exec_mode=None)

    print "Plotagem dos sinais em janelas concluída."


def execSeizureSignal():
    """Plotagem das crises presentes nos sinais."""
    import chbmit.signal
    import chbmit.utils

    argline.config()

    print "Plotando crises da base CHBMIT."
    f = chbmit.signal.plotCHBMITSizures
    fpattern = '{}_S{}-{}.png'
    fargs = None
    eargs = [('{}',)*2]

    save_dir = argline.OUTPUTDIR if argline.OUTPUTDIR else '.'

    chbmit.utils.defaultScript(f, fpattern, fargs, eargs, 'good',
                               save_dir, None)

    print "Plotagem das crises da base CHBMIT concluída."


def execSignalStatistics():
    """Plotagem da média e desvio padrão dos sinais utilizando janelas."""
    import chbmit.signal
    import chbmit.utils

    argline.config()

    print "Plotando sinais da base CHBMIT."
    f = chbmit.signal.plotCHBMITSignalStatistic
    fpattern = '{}_Stat_W{}_H{}.png'

    wsize = [256, 512, 1280, 2560]  # 1, 2, 5, e 10 segundo(s)
    hop = [128, 256, 640, 256]      # .5, 1, 2.5 e 1 segundo(s)
    fargs = [(w, h) for w, h in zip(wsize, hop)]
    eargs = None
    patients = 'good'

    save_dir = argline.OUTPUTDIR if argline.OUTPUTDIR else '.'
    chbmit.utils.defaultScript(f, fpattern, fargs, eargs, patients,
                               save_dir, 'full')

    print "Plotagem Concluída."


def execFourier():
    """Executa a transformada de Fourier nas bases de dados."""
    import chbmit.fourier
    import chbmit.utils

    argline.config()

    print "Iniciando Transformada de Fourier."

    print "Executando base de dados CHBMIT."
    f = chbmit.fourier.applyFourier
    fpattern = '{}_FT{}.png'
    patients = 'good'
    fargs = None
    eargs = [('',), ('1Delta',), ('2Theta',),
             ('3Alpha',), ('4Beta',), ('5Gamma',)]

    save_dir = argline.OUTPUTDIR if argline.OUTPUTDIR else '.'
    chbmit.utils.defaultScript(f, fpattern, fargs, eargs, patients, save_dir,
                               exec_mode='full')

    print "Plotagem da Transformada de Fourier concluída."


def execSTFT():
    """Executa a transformada curta de fourier (STFT) nas bases de dados."""
    import chbmit.fourier
    import chbmit.utils

    argline.config()

    print "Iniciando Execução: STFT."
    print "Processando base de dados: CHBMIT."
    f = chbmit.fourier.applySTFT
    fpattern = '{}_STFT_W{}_H{}{}.png'
    w = [128, 256, 640, 1280, 2560]   # janelas de 0.5, 1, 2.5, 5 e 10 segundos
    h = [ 64, 128, 320,  640, 512]    # deslocamento entre janelas
    fargs = [(k, j) for k, j in zip(w, h)]
    eargs = [('',), ('_0~20Hz',)]
    patients = 'good'

    save_dir = argline.OUTPUTDIR if argline.OUTPUTDIR else '.'
    chbmit.utils.defaultScript(f, fpattern, fargs, eargs, patients, save_dir,
                               exec_mode='full')

    print "Finalizando Execução: STFT."


def execWT():
    print "TODO: execWT."


def execRWE():
    print "TODO: execRWE."


def execWS():
    print "TODO: execWS."
