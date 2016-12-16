#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os


def validate_dir(path):
    """Faz a validação de um diretório. Após execução, o diretório existirá.

    Recebe um caminho para um diretório. Se *path* existir, nada será feito.
    Caso *path* não exista, será criado. Após execução de *validate_path*,
    *path* existirá.

    Parâmetros:
    -----------
    path: str
        string contendo o caminho do diretório a ser validado.
    """
    logging.debug("Validando diretório: {}".format(path))

    if not os.path.exists(path):
        try:
            logging.info("Criando diretório: {}".format(path))
            os.mkdir(path)
        except:
            errormsg = "Não foi possível criar diretório {}".format(path)
            logging.error(errormsg)
            raise OSError(errormsg)
    else:
        logging.debug("Diretório encontrado: {}".format(path))


def pathStructureValidation(root, subdir_list):
    """Verifica a existência e, se necessário, cria a estrutura de diretórios.

    Função responsável por analisar uma estrutura de diretórios, recebendo o
    diretório principal (*root*) e uma lista de subdiretórios. Caso os
    subdiretórios não existam, serão criados. Ao final da execução, sem erros,
    a árvore de diretórios, a partir de root, existirá.

    Parâmetros:
    -----------
    root: str
        string contendo o caminho para o diretório raiz. Se este não existir,
        tentará ser criado. Porém, caso o diretório pai de *root* também não
        exista, não será possível criar *root*.
    subdir_list: list
        lista de string. Cada elemento da lista deve conter o nome de um
        subdiretório de *root*. Caso este subdiretório não exista, será criado.
    """
    logging.debug("Verificando parâmetros de pathStructureValidation.")
    if not isinstance(root, str):
        errormsg = ("Parâmetro 'root' deve ser do tipo {}. "
                    "Tipo recebido: {}.".format(str, type(root)))
        logging.error(errormsg)
        raise ValueError(errormsg)

    if not isinstance(subdir_list, list):
        errormsg = ("Parâmetro 'subdir_list' deve ser do tipo {}. "
                    "Tipo recebido: {}.".format(list, type(subdir_list)))
        logging.error(errormsg)
        raise ValueError(errormsg)

    logging.debug("Validando estrutura de diretórios.")
    logging.debug("Verificando existência da raiz: {}".format(root))
    validate_dir(root)

    logging.debug("Percorrendo subdiretórios.")
    for subdir in subdir_list:
        path = os.path.join(root, subdir)
        validate_dir(path)

    logging.debug("Validação da estrutura de diretórios concluída.")


def extractFileLabel(fname):
    """Extrai apenas o nome dos arquivos, removendo extensão e caminho.

    Parâmetros:
    -----------
    fname: str
        nome ou caminho de um arquivo EDF.

    Retorno:
    --------
    str:
        nome do arquivo, sem caminho e sem extensão.
    """
    return fname.split('/')[-1].split('.')[0]


def cleanupFiles(files):
    """Remove os arquivos recebidos, se existirem.

    Recebe uma lista com nomes de arquivos, se estes arquivos existirem, serão
    removidos após a limpeza.

    Parâmetros:
    -----------
    files: list de str
        lista com caminhos para arquivos que serão removidos, se existirem.

    Nota:
    -----
    Utilizado para garantir execução completa dos scripts, ou seja, para saber
    quais arquivos foram criados na última execução do script.
"""
    logging.debug("Iniciando processo de limpeza...")
    for f in files:
        logging.debug("Verificando existência do arquivo: {}".format(f))
        if os.path.exists(f):
            os.remove(f)
            logging.info("Arquivo removido durante limpeza: {}".format(f))
