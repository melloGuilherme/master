#!/usr/bin/env python
# -*- coding: utf-8 -*-

import getopt
import logging
import os
import sys


# variáveis globais
OUTPUTDIR = None    # caminho para diretório de arquivos gerados


def _configLogLevel(log_level):
    """Configuração do nível de log.

    Parâmetros:
    -----------
    log_level: str
        string correspondente ao nível de log. Deve ser compatível com os
        níveis de log de *logging*.
    """
    log_level = getattr(logging, log_level.upper(), None)
    if not isinstance(log_level, int):
        raise ValueError("Nível inválido de log: {}".format(log_level))

    log = logging.getLogger()
    log.setLevel(log_level)


def _configLogFile(fname):
    """Define um arquivo de saída para armazenar as mensagens de log.

    Parâmetros:
    -----------
    fname: str
        caminho para um arquivo de log. Se necessário, será criado.
    """
    log = logging.getLogger()

    fmt = "%(levelname)s(%(funcName)s):\t%(message)s"
    formatter = logging.Formatter(fmt)

    fh = logging.FileHandler(fname, mode='w')
    fh.setFormatter(formatter)

    log.addHandler(fh)


def _configOutputDir(path):
    """Configura um diretório para salvar arquivos gerados.

    Parâmetros:
    -----------
    path: str
        string contendo o caminho para um diretório existente. Caso o diretório
        não exista, a execução será abortada.
    """
    global OUTPUTDIR
    if os.path.exists(path):
        OUTPUTDIR = path
    else:
        print ("Diretório para salvar saídas ('--outputdir') não existe: {}"
               "".format(path))
        sys.exit(2)


def config():
    """Cria e configura o arquivo de log com argumentos da linha de comando.

    Função responsável por configurar a execução dos scripts utilizando os
    parâmetros da linha de comando. Os parâmetros permitem a configuração de
    arquivos de log e arquivos de saída.
    """
    # extração das opções e argumentos passados pela linha de comandos
    options = 'h'
    long_options = ["help",
                    "loglevel=",
                    "logfile=",
                    "outputdir="]
    try:
        opts, args = getopt.getopt(sys.argv[1:], options, long_options)
    except getopt.GetoptError:
        print "Erro ao ler argumentos da linha de comandos."
        sys.exit(2)

    # configurações básicas de log
    log_format = "%(levelname)s(%(funcName)s):\t%(message)s"
    log_level = logging.INFO

    # extração e tratamento das opções desejadas
    for opt, value in opts:
        if opt in ('-h', '--help'):
            usage()
        if opt in ('--loglevel'):
            _configLogLevel(value)
        if opt in ('--logfile'):
            _configLogFile(value)
        if opt in ('--outputdir'):
            _configOutputDir(value)


def usage():
    """Imprime a mensagem de ajuda, informando as opções e o modo de usar."""
    print "Help:"
    print "usage: python <file.py> [options]"
    print "or: ./<file.py> [options]"
    print "\nOptions:"
    print "\t-h:\tdisplay help message."
    print "\n\t--loglevel:\tminimum log level to display."
    print "\t\toptions: ['debug'|'info'|'warning'|'error'|'critical']."
    print "\t\tdefault: 'info'."
    print "\n\t--logfile:\toutput log file."
    print "\t\tdefault: console."
    print "\n\t--outputdir:\troot directory for saving script's output."
    print "\t\tdefault: '.'"
    sys.exit(2)
