#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import mne
import os

from mestrado import datasetPathManipulation as dpm
from mestrado import pathManipulation as pm


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
    isso, quando aplicável, este canal de estímulo é removido. Outro canal
    removido é o T7-P7 por conter a mesma informação que P7-T7, pois é o mesmo
    sinal multiplicado por (-1).
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
        raw.drop_channels(['STI 014', 'T7-P7'], copy=False)
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


def getCHBMITFilesPath(patients='all'):
    """Retorna um dicionário com os caminhos absolutos dos arquivos EDF.

    Extrai todos os caminhos absolutos dos arquivos EDF dos pacientes
    desejados, estruturando em um dicionário de retorno. Cada chave (key) do
    dicionário representa um paciente diferente e o valor (value) seus
    respectivos arquivos EDF.

    Parâmetros:
    -----------
    patients: 'all'|'good'|str|list
        caso seja uma string, contém informação para um único paciente ou um
        grupo de pacientes. Caso seja uma lista, contém os rótulos dos
        pacientes desejados. Opções:
            'all': retornando todos os pacientes
            'good': retornando os pacientes sem arquivos corrompidos
            str: contendo o rótulo do paciente desejado.
            list: contendo os rótulos dos pacientes desejados.

    Retorno:
    --------
    dict:
        dicionário em que cada chave (key) representa um paciente diferente e o
        valor (value) seus respectivos arquivos EDF.

    Nota:
    -----
    Função utilizada para inicializar scripts sobre os arquivos EDF da base de
    dados CHBMIT.
    """
    # string com caminho absoluto para base de dados CHB
    dataset_path = dpm.getDatasetPath('chbmit')

    logging.debug("Validando lista de pacientes.")
    # lista contendo apenas o rótulo dos pacientes desejados
    patients_labels = dpm.getPatientsPath('chbmit', patients, False)
    logging.debug("Validação de pacientes concluida.")

    # dicionário contendo os rótulos dos pacientes (keys) e os respectivos
    # caminhos absolutos para os arquivos EDF (values). *values* é do tipo list
    logging.debug("Extraindo caminhos para arquivos EDF.")
    edf_dict = dpm.getFilesPath('chbmit', patients_labels, True)

    # verifica se o número de pacientes é compatível com o número de listas de
    # arquivos EDF. Devem conter o mesmo número de elementos.
    if len(patients_labels) != len(edf_dict):
        logging.debug("Lista de Pacientes: {}".format(patients_labels))
        logging.debug("Lista de arquivos EDF: {}".format(edf_dict.keys()))
        errormsg = ("Número de pacientes e quantidade de listas de arquivos "
                    "EDF são incompatíveis.")
        logging.error(errormsg)
        raise ValueError(errormsg)

    return edf_dict


# TODO: não suporta casos em que os argumentos extras não são previamente
# conhecidos. Alguns precisam abrir o EDF e calcular estes argumentos.
def _configFastExecution(pattern, args, ext_args):
    """Verifica se um arquivo deve ser executado, retornando um booleando.

    Prepara o ambiente para executar um arquivo em modo de execução rápida.
    Caso todos os arquivos de saída, gerados após a execução de um scritp,
    existam não há a necessidade de gerá-los novamente. Porém, se algum dos
    arquivos de saída não existir, todos deverão ser excluídos e gerados
    novamente. Esta função garante este comportamento, retornando um booleano,
    indicando se o arquivo de entrada necessita ser executado ou não.

    Parâmetros:
    -----------
    pattern: str
        string contendo o formato padrão dos arquivos de saída, porém, sem
        formatação. Ex: '{}_FT{}.png'
    args: list de (arg1, arg2, ...)
        lista de argumentos para formatação do padrão do arquivo de saída. Cada
        elemento da lista é uma tupla contendo os argumentos necessários para
        formatação (parâmetros para computação de cálculos, passados como
        parâmetros para outras funções).
    ext_args: list de (arg1, arg2, ...)
        lista de argumentos extras, também utilizados para formatar o padrão do
        arquivo de saída. Porém, estes são formatados ao final do padrão e não
        são utilizados para configurar outras funções (utilizados para
        modificar parâmetros de plotagem e não de computação).

    Retorno:
    --------
    bool:
        booleano indicando se o arquivo de entrada precisa, ou não, ser
        executado.
    """
    logging.info("Verificando se os arquivos já foram processados.")
    execute_file = False
    has_files = []
    if args:
        for arg in args:
            if ext_args:
                for earg in ext_args:
                    path = pattern.format(*(arg + earg))
                    if not os.path.exists(path):
                        execute_file = True
                    else:
                        has_files.append(path)
            else:
                path = pattern.format(*arg)
                if not os.path.exists(path):
                    execute_file = True
                else:
                    has_files.append(path)
    else:
        if not os.path.exists(pattern):
            execute_file = True

    if execute_file and has_files:
        pm.cleanupFiles(has_files)

    return execute_file


# TODO: não suporta casos em que os argumentos extras não são previamente
# conhecidos. Alguns precisam abrir o EDF e calcular estes argumentos.
def _configFullExecution(pattern, plabels, edf_dict, args, ext_args=None):
    """Remove arquivos já existentes que sejam compativeis com o padrão.

    Parâmetros:
    -----------
    pattern: str
        padrão de nomenclatura de arquivos, deve possuir campos para formatação
        com argumentos em *args*. Deve ser o padrão do caminho completo, com
        campos de formatação para rótulo do paciente, rótulo do arquivo e
        parâmetros de execução e plotagem. Ex: './root/{}/{}_FT{}_E{}.png'
    plabels: list
        lista de strings contendo apenas os rótulos dos pacientes.
    edf_dict: dict
        dicionário contendo os rótulos dos pacientes como chave, e uma lista
        com os caminhos para seus arquivos EDF como valor. Obtido por meio do
        método *getCHBMITFilesPath*
    args: list de (arg1, arg2, ...)
        lista de argumentos para formatação do padrão do arquivo de saída. Cada
        elemento da lista é uma tupla contendo os argumentos necessários para
        formatação (parâmetros para computação de cálculos, passados como
        parâmetros para outras funções).
    ext_args: list de (arg1, arg2, ...) (default: None)
        lista de argumentos extras, também utilizados para formatar o padrão do
        arquivo de saída. Porém, estes são formatados ao final do padrão e não
        são utilizados para configurar outras funções (utilizados para
        modificar parâmetros de plotagem e não de computação).
    """
    logging.info("Limpando Arquivos existentes.")
    files = []
    for plabel in plabels:
        for edf_path in edf_dict[plabel]:
            edf_label = pm.extractFileLabel(edf_path)
            if args is not None:
                for arg in args:
                    if ext_args:
                        for earg in ext_args:
                            f = pattern.format(plabel, edf_label, *(arg+earg))
                            files.append(f)
                    else:
                        f = pattern.format(plabel, edf_label, *arg)
                        files.append(f)
            elif ext_args:
                for earg in ext_args:
                    f = pattern.format(plabel, edf_label, *earg)
                    files.append(f)
            else:
                f = pattern.format(plabel, edf_label)
                files.append(f)
    pm.cleanupFiles(files)


def defaultScript(func, fname_pat, fargs, ext_args=None, patients='good',
                  save_dir='output', exec_mode='full', **kwargs):
    """Execução de instruções comuns aos scripts sobre a base de dados CHBMIT.

    Esta função deve ser utilizada como um esqueleto para outras funções que
    executam algum tipo de computação sobre a base de dados CHBMIT. Ao fazer a
    chamada a esta função, serão selecionados os arquivos de entrada desejados.
    Em seguida, serão verificados os arquivos de saída e processados de acordo
    com o modo de execução. Para cada arquivo de entrada, será executada a
    função passada por *func*, passando os argumentos em *fargs*, *ext_args* e
    */*/*kwargs*. Ao final os arquivos gerados serão verificados.

    Parâmetros:
    -----------
    func: função
        função que será executada para cada arquivo de entrada. A ordem dos
        parâmetros de *func* precisam obedecer um determinado formato, descrito
        nas notas.
    fname_pat: str
        string contendo o padrão para salvar o arquivo de saída com campos de
        formatação. Este padrão deve contér apenas o padrão para o nome do
        arquivo, abaixo de *save_path/patient/*. O número de campos para
        formatação deve ser *len(fargs[0])+1*, de modo que o primeiro campo
        corresponda ao rótulo do arquivo e os demais campos referentes aos
        parâmetros de execução de *func*.
    fargs: list de (arg1, arg2, ...)
        lista de tuplas com argumentos para formatação dos arquivos de saída e
        execução de *func*. Cada tupla corresponde a um arquivo de saída
        diferente, e cada elemento da tupla a um argumento de formatação.
    ext_args: list de (arg1, arg2, ...) (default: None)
        lista de tuplas com argumentos extras utilizados para cofiguração de
        plotagens, também utilizado para a formatação dos arquivos de saída.
    patients: 'all'|'good'|str|list (default: 'all')
        caso seja uma string, contém informação para um único paciente ou um
        grupo de pacientes. Caso seja uma lista, contém os rótulos dos
        pacientes desejados. Opções:
            'all': retornando todos os pacientes
            'good': retornando os pacientes sem arquivos corrompidos
            str: contendo o rótulo do paciente desejado.
            list: contendo os rótulos dos pacientes desejados.
    save_dir: str (default: 'output')
        string contendo o diretório em que serão salvos os arquivos de saída.
    exec_mode: 'full'|'fast' (default: 'full')
        modo de execução do script. Caso 'fast', arquivos de entrada já
        computados não serão computados novamente. Caso 'full', arquivos de
        saída já existentes serão deletados e gerados novamente.
    **kwargs:
        argumentos passados para a função recebida pelo parâmetro *func*. Os
        argumentos válidos dependem de *func*.

    Notas:
    ------
    *func* é uma função que executa algum tipo de computação sobre um único
    arquivo EDF, a qual deve obedecer uma regra para a ordem de parâmetros.
    Assimi, a função *func* deve seguir a seguinte especificação:

    func(raw, file_pattern, *args, ext_args=ext_args, **kwargs)
    raw: mne.Raw
        objeto Raw contendo informações do sinal
    file_pattern: str
        padrão para salvar arquivos de saída. Já com o caminho completo e
        primeiro argumento do nome do arquivo (rótulo) preencidos, necessitando
        apenas preencher com os parâmetros de execução e plotagem.
    *args: tupla de argumentos
        sequência de argumentos. O número de argumentos deve ser compatível com
        as tuplas em *fargs*.
    ext_args: list de (arg1, arg2, ...)
        são argumentos para plotagem.
    **kwargs:
        argumentos com palavra-chave.
    """
    logging.info("Iniciando execução do script: {}.".format(func.__name__))

    # extrai os caminhos absolutos dos EDF
    edf_dict = getCHBMITFilesPath(patients)

    # lista ordenada dos rótulos dos pacientes
    plabels = edf_dict.keys()
    plabels.sort()

    # cria a estrutura de arquivos para salvar os resultados
    logging.info("Validando/Criando caminhos para salvar resultados.")
    pm.pathStructureValidation(save_dir, plabels)
    logging.info("Caminhos validados/criados.")

    # padão para o nome dos arquivos (base/paciente/arquivo)
    save_pattern = os.path.join(save_dir, '{}', fname_pat)

    # limpando arquivos existentes (caso execução completa)
    if exec_mode == 'full':
        _configFullExecution(save_pattern, plabels, edf_dict, fargs, ext_args)

    logging.debug("Percorrendo lista de pacientes.")
    for plabel in plabels:
        logging.info("Executando dados do paciente {}".format(plabel))

        logging.debug(("Extraíndo sumário de crises do paciente: {}"
                       "".format(plabel)))
        ppath = os.path.dirname(edf_dict[plabel][0])
        summary_path = os.path.join(ppath, "{}-summary.txt".format(plabel))
        summary_dict = summaryFileParser(summary_path)

        # percorre todos os arquivos .edf
        for edf_path in edf_dict[plabel]:
            print "Executando {}".format(edf_path)

            # extrai o nome do arquivo sem a extensão .edf
            edf_label = pm.extractFileLabel(edf_path)
            logging.debug("Nome do arquivo EDF: {}".format(edf_label))

            # nome do arquivo a ser salva a imagem
            if fargs:
                le = len(fargs[0])
                if ext_args:
                    le += len(ext_args[0])

                # mantém campos de esntrada sem formatação
                entries = ('{}',)*le

                file_pattern = save_pattern.format(plabel, edf_label, *entries)
            elif ext_args:
                le = len(ext_args[0])
                entries = ('{}',)*le

                file_pattern = save_pattern.format(plabel, edf_label, *entries)
            else:
                file_pattern = save_pattern.format(plabel, edf_label)

            # verificando se é necessário executar arquivo
            if exec_mode == 'fast':
                to_exec = _configFastExecution(file_pattern, fargs, ext_args)
                if not to_exec:
                    logging.info(("Arquivo não será processado: {}"
                                  "".format(edf_path)))
                    continue

            logging.info("Abrindo arquivo EDF: {}".format(edf_path))
            raw = openEDF(edf_path, summary_dict)

            if fargs:
                for args in fargs:
                    func(raw, file_pattern, *args, ext_args=ext_args, **kwargs)
            else:
                func(raw, file_pattern, ext_args=ext_args, **kwargs)

    # TODO: Melhorar a verificação de arquivos gerados (código muito ruim)
    logging.info("Verificando existência de arquivos criados.")
    for plabel in plabels:
        for edf_path in edf_dict[plabel]:
            edf_label = pm.extractFileLabel(edf_path)
            if fargs:
                for args in fargs:
                    if ext_args:
                        for eargs in ext_args:
                            img_path = save_pattern.format(plabel, edf_label,
                                                           *(args+eargs))
                            if os.path.exists(img_path):
                                logging.info("Arquivo OK: {}".format(img_path))
                            else:
                                logging.warning("PROBLEMAS AO GERAR IMAGEM. "
                                                "ARQUIVO NÃO ENCONTRADO: {}"
                                                "".format(img_path))
                    else:
                        img_path = save_pattern.format(plabel, edf_label,
                                                       *args)
                        if os.path.exists(img_path):
                            logging.info("Arquivo OK: {}".format(img_path))
                        else:
                            logging.warning(("PROBLEMAS AO GERAR IMAGEM. "
                                             "ARQUIVO NÃO ENCONTRADO: {}"
                                             "".format(img_path)))
            else:
                if ext_args:
                    for eargs in ext_args:
                        img_path = save_pattern.format(plabel, edf_label,
                                                       *(eargs))
                        if os.path.exists(img_path):
                            logging.info("Arquivo OK: {}".format(img_path))
                        else:
                            logging.warning("PROBLEMAS AO GERAR IMAGEM. "
                                            "ARQUIVO NÃO ENCONTRADO: {}"
                                            "".format(img_path))
                else:
                    img_path = save_pattern.format(plabel, edf_label)
                    if os.path.exists(img_path):
                        logging.info("Arquivo OK: {}".format(img_path))
                    else:
                        logging.warning("PROBLEMAS AO GERAR IMAGEM. ARQUIVO "
                                        "NÃO ENCONTRADO: {}".format(img_path))
