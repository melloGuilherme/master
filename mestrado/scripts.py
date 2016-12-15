#!/usr/bin/env python
# -*- coding: utf-8 -*-

import chbmit
import logDefinitions
import sys

def execDatasetFileVerifier():
    """Verifica a integridade das bases de dados.

    Para cada base de dados utilizada, é chamada uma função diferente. Esta
    função faz as chamadas de forma ordenada, mantendo registros de log.

    Nota:
    -----
    Os parâmetros de configuração são passados por linha de comando. Para mais
    informações, ver o módulo *logDefinitions*.
    """
    logDefinitions.logConfig(sys.argv[1:])

    print "Iniciando verificação de arquivos."

    print "Verificando Base: CHBMIT."
    chbmit.verifyCHBMITFiles()

    print "Verificação Concluída!"
