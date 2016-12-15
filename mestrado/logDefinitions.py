#!/usr/bin/env python
# -*- coding: utf-8 -*-

import getopt
import logging
import sys


def logConfig(argv):
    """Cria e configura o arquivo de log com argumentos da linha de comando.

    Função responsável por criar e configurar um arquivo de log que será
    utilizado para manter os registros de execução dos experimentos. Melhorando
    o rastreamento em casos de falha. É possível utilizar argumentos pela linha
    de comandos para definir algumas configurações de log.

    Parâmetros:
    -----------
    argv: list
        lista contendo os argumentos passados por linha de comando.
        -h          imprime uma mensagem de ajuda.
        --loglevel  define o menor nível de log a ser reportado.
        --logfile   nome do arquivo de saída do log.
    """
    # extração das opções e argumentos passados pela linha de comandos
    try:
        opts, args = getopt.getopt(argv, "h", ["loglevel=", "logfile="])
    except getopt.GetoptError:
        print "Erro ao ler argumentos da linha de comandos."
        sys.exit(2)

    loglevel = None     # nível a ser mostrado no arquivo de log
    logfile = None      # arquivo de log

    # extração e tratamento das opções desejadas
    for opt, value in opts:
        if opt in ('-h'):
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
            sys.exit(2)

        if opt in ('--loglevel'):
            loglevel = getattr(logging, value.upper(), None)

            if not isinstance(loglevel, int):
                raise ValueError("Nível inválido de log: {}".format(loglevel))

        if opt in ('--logfile'):
            logfile = value

    # caso necessário, define o nível de log como INFO
    if loglevel is None:
        loglevel = logging.INFO

    # faz a configuração básica de log
    log_format = "%(levelname)s(%(funcName)s):\t%(message)s"
    if logfile is None:
        # imprime no console
        logging.basicConfig(level=loglevel, format=log_format)
    else:
        # salva em um arquivo
        logging.basicConfig(level=loglevel, format=log_format,
                            filename=logfile, filemode='w')
