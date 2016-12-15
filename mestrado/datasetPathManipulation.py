#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ConfigParser
import logging
import os


def getDatasetPath(dataset_label):
    """Retorna o caminho para uma base de dados, se este existir.

    Recebe uma string contendo o rótulo da base de dados (no arquivo de
    configuração dataset.cfg). Verifica se o caminho para a base de dados
    existe e retorna. Caso o caminho seja inválido, um erro é lançado.

    Parâmetros:
    -----------
    dataset_label: str
        rótulo da base de dados (seção) dentro do arquivo de configuração
        (dataset.cfg).

    Retorno:
    --------
    str:
        string contendo o caminho absoluto para a base de dados.

    Exceptions:
    -----------
    ValueError:
        erro lançado caso o caminho para a base de dados não exista.
    """
    logging.debug("Executando getDatasetPath().")
    config = ConfigParser.ConfigParser()
    config.read('dataset.cfg')
    dataset_path = config.get(dataset_label, 'path')

    logging.debug(("Procurando base de dados {} "
                   "em: {}".format(dataset_label, dataset_path)))

    if os.path.exists(dataset_path):
        logging.debug("Base de dados encontrada.")
        logging.debug("Retornando caminho para base de dados.")
        return dataset_path
    else:
        msg = ("Caminho não encontrado. "
               "Verificar caminho para a base de dados {} "
               "no arquivo de configuração!".format(dataset_path))

        logging.error(msg)
        raise ValueError(msg)


def getPatientsLabel(dataset_label, good_data=True):
    """Retorna uma lista de conjuntos de dados pré-selecionados.

    Função responsável por verificar a existência e retornar os rótulos dos
    conjuntos desejados, com base no arquivo de configuração (dataset.cfg).
    Caso o caminho absoluto para algum conjunto não exista, o mesmo é excluído
    da lista de retorno.

    Parâmetros:
    -----------
    dataset_label: str
        rótulo da base de dados (seção) dentro do arquivo de configuração
        (dataset.cfg).
    good_data: bool (default:True)
        define qual conjunto de dados deve ser retornado, com base no arquivo
        de configuração (dataset.cfg). Se True, retorna os conjuntos listados
        em *good-data*. Caso False, retorna os conjuntos listados em
        *all-data*.

    Retorno:
    --------
    list:
        lista contendo os rótulos dos conjuntos de dados selecionados.

    Notas:
    ------
    Conjuntos são entendidos como pastas que contém arquivos (dados)
    semelhantes, como os arquivos de um mesmo paciente.
    """
    logging.debug("Executando getPatientsLabel()")

    # verifica a existência e retorna o caminho para a base de dados
    dataset_path = getDatasetPath(dataset_label)

    # leitura do arquivo de configuração
    config = ConfigParser.ConfigParser()
    config.read('dataset.cfg')

    # seleciona os rótulos desejados
    if good_data:
        logging.debug(("Selecionando rótulos dos pacientes  "
                       "sem arquivos corrompidos."))
        labels = config.get(dataset_label, 'good-data').split(',')
    else:
        logging.debug("Selecionando rótulos de todos os pacientes.")
        labels = config.get(dataset_label, 'all-data').split(',')

    labels.sort()

    logging.debug("Rótulos selecionados:")
    for label in labels:
        logging.debug(label)

    logging.debug("Verificando existência dos rótulos.")
    for label in labels:
        path = os.path.join(dataset_path, label)
        logging.debug("Verificando {}".format(path))

        if not(os.path.exists(path) and os.path.isdir(path)):
            logging.error("Não foi possível encontrar: {}".format(path))
            logging.error("Removendo '{}' da lista de retorno.".format(label))
            labels.remove(label)

    return labels


def getPatientsPath(dataset_label, patients, abs_path=True):
    """Verifica os caminhos para os pacientes, retonrando os caminhos válidos.

    Esta função faz a validação do parâmetro *patients* para selecionar um
    conjunto de pacientes válidos e existentes. Após a validação, os caminhos
    absolutos (ou apenas os rótulos) para as pastas dos pacientes é construída
    e retornada.

    Parâmetros:
    -----------
    dataset_label: str
        rótulo da base de dados (seção) dentro do arquivo de configuração
        (dataset.cfg).
    patients: 'all'|'good'|str|list
        caso seja uma string, contém informação para um único paciente ou um
        grupo de pacientes. Caso seja uma lista, contém os rótulos dos
        pacientes desejados. Opções:
            'all': retornando todos os pacientes
            'good': retornando os pacientes sem arquivos corrompidos
            str: contendo o rótulo do paciente desejado.
            list: contendo os rótulos dos pacientes desejados.
    abs_path: True|False (default: True)
        determina se o retorno contém apenas os rótulos válidos, passados pelo
        parâmetro *patients* (caso False), ou os caminhos absolutos (caso True)

    Retorno:
    --------
    list:
        lista contendo os rótulos dos pacientes desejados.
    """
    patients_labels = None
    if patients == 'all':
        msg = "Criando lista com todos os pacientes (good_data=False)."
        logging.debug(msg)
        patients_labels = getPatientsLabel(dataset_label, good_data=False)

    elif patients == 'good':
        msg = ("Criando lista com pacientes sem arquivos "
               "corrompidos (good_data=True).")
        logging.debug(msg)
        patients_labels = getPatientsLabel(dataset_label, good_data=True)

    elif isinstance(patients, str):
        logging.debug("Criando lista com paciente {}.".format(patients))
        patients_labels = [patients]

    elif isinstance(patients, list):
        logging.debug("Criando lista de pacientes com a lista de entrada.")
        patients_labels = patients

    # verifica se todos os pacientes (caminhos) existem
    logging.debug("Verificando lista com rótulos de pacientes gerada.")
    if patients_labels is None:
        errormsg = ("Não foi possível recuperar lista de pacientes. "
                    "Verifique o parâmetro passado em patients: "
                    "{}".format(patients))
        logging.error(errormsg)
        raise ValueError(errormsg)

    ret = []
    dataset_path = getDatasetPath(dataset_label)
    for patient in patients_labels:
        path = os.path.join(dataset_path, patient)
        if not os.path.exists(path):
            logging.warning("O caminho não existe: {}".format(path))
            logging.warning(("Removendo paciente da lista de retorno: "
                             "{}.".format(patient)))
            continue

        if abs_path:
            ret.append(path)
        else:
            ret.append(patient)

    if len(ret) == 0:
        logging.warning("Nenhum paciente correspondente foi encontrado.")
        logging.warning("Retornando uma lista vazia.")

    logging.debug("Verificação e extração de rótulos finalizada.")
    return ret


def getFilesPath(dataset_label, patients, abs_path=True):
    """Extrai e retorna os caminhos/rótulos dos arquivos dos conjunto de dados.

    Esta função verifica, a partir dos rótulos dos pacientes, quais são os
    arquivos de dados presentes em cada conjunto desejado. Caso algum rótulo de
    algum conjunto seja passado errado, este será descartado, gerando um aviso
    (warning) na saída de log (logging). O retorno consiste de uma matriz
    (vetor bidimensional), em que cada elemento é uma lista contendo os
    caminhos para os arquivos de dados para cada conjunto de dados.

    Parâmetros:
    -----------
    dataset_label: str
        rótulo da base de dados (seção) dentro do arquivo de configuração
        (dataset.cfg).
    patients: 'all'|'good'|str|list
        caso seja uma string, contém informação para um único paciente ou um
        grupo de pacientes. Caso seja uma lista, contém os rótulos dos
        pacientes desejados. Opções:
            'all': retornando todos os pacientes
            'good': retornando os pacientes sem arquivos corrompidos
            str: contendo o rótulo do paciente desejado.
            list: contendo os rótulos dos pacientes desejados.
    abs_path: True|False (default: True)
        Modifica como o arquivo de dados será retornado. True faz com que o
        caminho absoluto, até o arquivo, seja retornado. False retorna apenas
        o nome do arquivo.

    Retorno:
    --------
    dict
        dicionário contendo os conjuntos válidos (key) e sua lista (value) de
        caminhos para os arquivos de dados.
    """
    logging.debug("Executando getEdfFileName()")

    # verifica existência e retorna o caminho para a base de dados
    dataset_path = getDatasetPath(dataset_label)

    config = ConfigParser.ConfigParser()
    config.read('dataset.cfg')
    file_type = config.get(dataset_label, 'file-type')
    ext = ".{}".format(file_type)   # data file extension

    logging.debug(("Construindo lista com rótulos dos "
                   "pacientes que serão buscados."))
    patients_labels = getPatientsPath(dataset_label, patients, False)

    files = {}
    logging.debug("Construindo dicionário de arquivos.")
    for patient in patients_labels:
        path = os.path.join(dataset_path, patient)
        logging.debug("Verificando arquivos em: {}".format(path))

        logging.debug("Extraindo apenas os nomes dos arquivos de dados.")
        patient_files = [f for f in os.listdir(path) if f.endswith(ext)]
        patient_files.sort()

        if abs_path:
            logging.debug("Construção com caminho completo.")
            patient_files = [os.path.join(path, f) for f in patient_files]

        logging.debug("Adicionando arquivos encontrados para retorno.")
        files[patient] = patient_files

    if len(files) == 0:
        logging.error(("Não foram encontrados arquivos "
                       "{} para: {}".format(ext, patients)))
        logging.error("Retornando dicionário vazio.")
    else:
        logging.debug("Retornando arquivos encontrados.")

    return files


def getAnnotationsPath(dataset_label, patients, abs_path=True):
    """Extrai os caminhos para as anotações. Retornando um dicionário.

    Esta função verifica, a partir dos rótulos dos pacientes, quais são os
    arquivos de anotações presentes na base de dados de cada paciente desejado.
    Caso algum rótulo (paciente) seja passado errado, este será descartado,
    gerando um aviso (warning) na saída de log (logging). O retorno consiste de
    um dicionário com os nomes dos pacientes (keys) e uma lista (values) com os
    nomes dos seus arquivos de anotações.

    Parâmetros:
    -----------
    dataset_label: str
        rótulo da base de dados (seção) dentro do arquivo de configuração
        (dataset.cfg).
    patients: 'all'|'good'|str|list
        caso seja uma string, contém informação para um único paciente ou um
        grupo de pacientes. Caso seja uma lista, contém os rótulos dos
        pacientes desejados. Opções:
            'all': retornando todos os pacientes
            'good': retornando os pacientes sem arquivos corrompidos
            str: contendo o rótulo do paciente desejado.
            list: contendo os rótulos dos pacientes desejados.
    abs_path: True|False. Modifica como o sumário será retornado. True faz com
        que o caminho inteiro, até o arquivo, seja retornado. False retorna
        apenas o nome do arquivo.

    Retorno:
    --------
    dict
        dicionário contendo os pacientes desejados (key) e sua lista (value) de
        arquivos de anotação.
"""
    logging.debug("Executando getAnnotationsPath")

    # extração e validação do caminho para a base de dados
    dataset_path = getDatasetPath(dataset_label)

    # extração e validação dos rótulos dos pacientes
    patients_labels = getPatientsPath(dataset_label, patients, False)

    config = ConfigParser.ConfigParser()
    config.read('dataset.cfg')
    ext = config.get(dataset_label, 'annot-type')

    annot_names = {}
    logging.debug("Criando dicionário com caminhos dos arquivos de anotações.")
    for patient in patients_labels:
        path = os.path.join(dataset_path, patient)
        logging.debug("Procurando anotações em: {}".format(path))

        logging.debug("Extraindo apenas o nome do arquivo de sumário.")
        annot_names[patient] = [f for f in os.listdir(path) if f.endswith(ext)]

        if abs_path:
            logging.debug("Inserindo caminho completo para sumário.")
            annot_names[patient] = [os.path.join(path, f)
                                    for f in annot_names[patient]]

    # verificando existência dos sumários
    logging.debug(("Verificando consistência dos "
                   "arquivos de sumário encontrados."))

    if len(annot_names) != len(patients_labels):
        logging.error("Erro ao extrair arquivos de sumário.")
        errormsg = ("Dicionário de anotações e lista de pacientes "
                    "com tamanhos diferentes.")
        logging.error(errormsg)
        raise ValueError(errormsg)

    for patient in annot_names:
        for annot in annot_names[patient]:
            if abs_path:
                path = annot
            else:
                path = os.path.join(dataset_path, patient, annot)

            if not os.path.exists(path):
                logging.warning(("Não foi possivel encontrar o caminho: "
                                 "{}".format(path)))
                logging.warning("Removendo arquivo não encontrado.")
                annot_names[patient].remove(annot)

    logging.debug("Verificação de existência concluída.")

    if len(annot_names) == 0:
        logging.warning("Nenhum arquivo de anotações encontrado.")
        logging.warning("Retornando dicionário vazio.")
    else:
        logging.debug("Retornando arquivos de anorações encontrados.")

    return annot_names


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
