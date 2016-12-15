#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import mne
import os


def summaryFileParser(summary_path):
    """Extrai as informações das crises dos arquivos de sumário, retornando em
    um dicionário.

    Função desenvolvida para extrair as informações sobre as crises dos
    arquivos de sumário, verificando sua existência. As informações extraídas
    contém dados sobre início, fim, duração e número de crises nos arquivos
    edf, retornando estes dados em um dicionário.

    Parâmetros:
    -----------
    summary_path: str
        string contendo o caminho para o arquivo sumário.

    Retorno:
    --------
    dict:
        dicionário contendo as informações extraídas do arquivo de sumário,
        estruturadas da seguinte forma:
        d[fname][info]
        fname: str
            string com o nome do arquivo .edf (apenas o nome do arquivo)
        info: str
            string com um tipo de informação extraída. Opções:
            ['annot_num']: inteiro com o número de anotações (crises)
            ['annot_start']: lista com os tempos de início das anotações
                (em segundos)
            ['annot_end']: lista com os tempos de término das anotações
                (em segundos)

    Nota:
    -----
    Arquivos de sumário: estão presentes nas pastas de cada paciente e possuem
        informações sobre as anotações dos arquivos .edf, como: a quantidade de
        crises presentes em cada arquivo e os tempos de início e fim para cada
        crise.
    As informações extraídas são importantes para criação de anotações ao ler
        os arquivos .edf utilizando a biblioteca *mne*, permitindo melhor
        manipulação dos sinais.
    """
    logging.debug("Executando summaryFileParser.")

    if not isinstance(summary_path, str):
        errormsg = ("O parâmetro de entrada da função summaryFileParser deve "
                    "ser do tipo str. Recebeu: {}".format(type(summary_path)))
        logging.error(errormsg)
        raise ValueError(errormsg)

    logging.debug("Verificando existência do sumário: {}".format(summary_path))
    if not os.path.exists(summary_path):
        errormsg = ("Não foi possível encontrar o arquivo ",
                    "{}".format(summary_path))
        logging.error(errormsg)
        raise ValueError(errormsg)
    else:
        logging.debug("Sumário encontrado.")

    logging.debug("Abrindo sumário.")
    summary_file = open(summary_path)
    summary_data = {}

    # percorre todo o arquivo, linha por linha, procurando por informações
    # sobre as anotações (crises) de cada arquivo .edf
    logging.debug("Percorrendo linhas do sumário")
    line = summary_file.readline()
    while line != '':
        # procura a linha que contém o nome do arquivo .edf
        logging.debug("Procurando linha com nome do arquivo edf.")
        if line.find("File Name:") >= 0:
            logging.debug("Extraindo nome do arquivo edf.")
            fname = line.split()[-1]    # extrai, da linha, o nome do arquivo
            seizures_start = []         # tempos de início das crises
            seizures_end = []           # tempos de término das crises

            # procura pelo número de críses presentes no arquivo 'fname' apenas
            logging.debug(("Procurando informações sobre as crises em ",
                           "{}".format(fname)))
            while line.find("Number of Seizures in File:") < 0:
                line = summary_file.readline()

            nseizures = int(line.split()[-1])
            logging.debug("Número de crises: {}.".format(nseizures))

            # extrai informações sobre cada crise presente no sinal (início e
            # fim). Existem dois tipos de padão nos arquivos summary.
            for seiz_i in range(1, nseizures+1):
                pattern1 = "Seizure Start Time:"
                pattern2 = "Seizure "+str(seiz_i)+" Start Time:"

                # extrai informação de início da crise 'seiz_i'
                while line.find(pattern1) < 0 and line.find(pattern2) < 0:
                    line = summary_file.readline()

                seizures_start.append(int(line.split()[-2]))

                pattern1 = "Seizure End Time:"
                pattern2 = "Seizure "+str(seiz_i)+" End Time:"
                # extrai informação de término da crise 'seiz_i'
                while line.find(pattern1) < 0 and line.find(pattern2) < 0:
                    line = summary_file.readline()

                seizures_end.append(int(line.split()[-2]))

            # as anotações dos arquivos .edf estão ordenadas e aparecem apenas
            # uma vez. Por isso, não devem existir chaves anteriores com mesmos
            # nomes
            if fname in summary_data:
                errormsg = ("ERRO: Não deveria conter esta chave "
                            "(key: {})".format(fname))
                logging.error(errormsg)
                raise ValueError(errormsg)

            logging.debug(("Criando entrada no dicionário ",
                           "com informações extraídas."))

            summary_data[fname] = {}
            summary_data[fname]["annot_num"] = nseizures
            summary_data[fname]["annot_start"] = seizures_start
            summary_data[fname]["annot_end"] = seizures_end

        line = summary_file.readline()

    if len(summary_data) == 0:
        logging.warning(("Retornando dicionário vazio. "
                         "Nenhuma informação de crise foi extraída."))
    else:
        logging.debug("Retornando dicionário com informações encontradas.")
    return summary_data


def openEDF(edf_path, annot_dict=None):
    """Abre um arquivo EDF devidamente anotado. Retornando um objeto Raw.

    Faz a leitura de um arquivo EDF, utilizando a biblioteca mne. Recebe o
    endereço absoluto para o arquivo EDF e, se necessário, um dicionário com as
    anotações do sinal. Retorna um objeto do tipo Raw (mne) devidamente anotado
    e sem o canal de estímulo.

    Parâmetros:
    -----------
    edf_path: str
        string contendo o caminho absoluto para um arquivo EDF.
    annot_dict: dict (default:None)
        dicionário que contém as informações sobre as anotações do sinal. Para
        mais informações sobre o formato (estrutura) do dicionário ver
        *summaryFileParser*.

    Retorno:
    --------
    mne.Raw:
        objeto Raw da biblioteca *mne*, contendo as informações sobre o sinal e
        suas anotações.

    Nota:
    -----
    O canal de estímulo ('STI 014') é criado pela biblioteca mne de forma
    automatica, devido à uma replicação do canal T8-P8 na base de dados. Com
    isso, quando aplicável, este canal de estímulo é removido.
"""
    logging.debug("Executando openEDF para {}".format(edf_path))

    logging.debug("Abrindo arquivo EDF.")
    if not os.path.exists(edf_path):
        errormsg = "Não foi possível encontrar o arquivo: {}".format(edf_path)
        logging.error(errormsg)
        raise ValueError(errormsg)

    # abre o arquivo edf
    raw = mne.io.read_raw_edf(edf_path, preload=True, verbose=False)

    logging.debug("Removendo canal de estímulo criado pela biblioteca mne.")
    try:
        raw.drop_channels(['STI 014'], copy=False)
        logging.debug("Canal de estímulo removido.")
    except:
        logging.warning("{} não contém canal de estímulo".format(edf_path))

    # verifica se não exite um dicionário de anotações
    logging.debug("Verificando anotações.")
    if annot_dict is None:
        logging.debug("Não foram passadas anotações para este sinal.")
        logging.debug("Retornando objeto Raw sem anotações.")
        return raw

    # verifica se exitem anotações no arquivo edf aberto com base no dicionário
    logging.debug("Inserindo anotações no sinal.")
    dict_key = edf_path.split('/')[-1]
    if dict_key in annot_dict and annot_dict[dict_key]['annot_num'] > 0:
        start = annot_dict[dict_key]['annot_start']
        end = annot_dict[dict_key]['annot_end']
        duration = [f-s for s, f in zip(start, end)]

        annot = mne.Annotations(start, duration, "seizures")
        raw.annotations = annot
    logging.debug("Anotações inseridas.")

    logging.debug("Retornando objeto Raw com anotações.")
    return raw
