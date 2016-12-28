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
                               save_dir=save_dir, exec_mode='full')


def execSignalStatistics():
    print "TODO: execSignalStatistics."


def execFourier():
    print "TODO: execFourier."
    # """Executa a transformada de Fourier nas bases de dados."""
    # argline.config()

    # print "Iniciando Transformada de Fourier."

    # print "Executando base de dados CHBMIT."
    # sp = argline.OUTPUTDIR if argline.OUTPUTDIR else '.'
    # chbmit.applyFourier(patients='good', save_path=sp, exec_mode='full')


def execSTFT():
    print "TODO: execSTFT."


def execWT():
    print "TODO: execWT."


def execRWE():
    print "TODO: execRWE."


def execWS():
    print "TODO: execWS."
