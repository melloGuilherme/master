#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ConfigParser
import datasetPathManipulation as dpm
import itertools as itt
import logging
import mne
import numpy as np
import os
import pathManipulation as pm
import plotModels


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


def verifyCHBMITFiles():
    """ Verifica quais arquivos EDF da base de dados CHBMIT abrem corretamente.

    Função desenvolvida para verificar quais arquivos da base de dados CHBMIT
    abrem corretamente. Por motivos desconhecidos, alguns arquivos EDF possuem
    canais com rótulos repetidos e incoerentes, causando erros ao lê-los com a
    biblioteca *mne*. Ao verificar quais arquivos podem, ou não, serem abertos,
    imprime em um arquivo de log (se definido) quais arquivos puderam ser
    abertos e quais não foram.
    """
    # cria objeto para leitura das configurações da base CHBMIT
    cfg = ConfigParser.ConfigParser()
    cfg.read('dataset.cfg')

    # verifica existência do caminho para a base de dados
    dataset_path = cfg.get('chbmit', 'path')
    if not os.path.exists(dataset_path):
        msg = ("Não foi possível encontrar a base de dados ",
               "em {}".format(dataset_path))
        logging.error(msg)
        raise OSError(msg)

    logging.info("Localização da base de dados: {}\n".format(dataset_path))

    # seleciona as pastas de todos os pacientes (padrão: chbXX)
    patients_label = [l for l in os.listdir(dataset_path) if not l.find("chb")]
    patients_label.sort()

    logging.debug("Pacientes encontrados:")
    for p in patients_label:
        logging.debug(p)

    # lista de pacientes que todos os arquivos EDF abriram
    good_data = []
    for label in patients_label:
        # seleciona apenas os arquivos .edf para o paciente *label*
        patient_path = os.path.join(dataset_path, label)

        logging.info("Examinando paciente em: {}".format(patient_path))
        print "Examinando paciente em: {}".format(patient_path)

        edf_list = [edf for edf in os.listdir(patient_path)
                    if edf.lower().endswith(".edf")]
        edf_list.sort()

        logging.debug("Arquivos EDF encontrados para: {}".format(patient_path))
        for edf in edf_list:
            logging.debug(edf)

        # verifica quais arquivos não podem ser abertos e imprime
        for edf in [os.path.join(patient_path, edf) for edf in edf_list]:
            can_open = True
            try:
                logging.debug("Abrindo edf: {}".format(edf))
                mne.io.read_raw_edf(edf, verbose=False)
            except:
                logging.warning("[Erro ao abrir]: {}".format(edf))
                can_open = False

        if can_open:
            good_data.append(label)

    logging.info("Arquivos não corrompidos:")
    for p in good_data:
        logging.info(p)


def _getCHBMITFilesPath(patients='all'):
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

    logging.info("Validando lista de pacientes.")
    # lista contendo apenas o rótulo dos pacientes desejados
    patients_labels = dpm.getPatientsPath('chbmit', patients, False)
    logging.info("Validação de pacientes concluida.")

    # dicionário contendo os rótulos dos pacientes (keys) e os respectivos
    # caminhos absolutos para os arquivos EDF (values). *values* é do tipo list
    logging.info("Extraindo caminhos para arquivos EDF.")
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


def _configFastExecution(pattern, args):
    """Verifica se um arquivo deve ser executado, retornando um booleando.

    Prepara o ambiente para executar um arquivo em modo de execução rápida.
    Caso todos os arquivos de saída, gerados após a execução de um scritp,
    existam não há a necessidade de executá-lo novamente. Porém, se algum dos
    arquivos de saída não existir, todos são excluídos e gerados novamente.
    Retornando um booleano, indicando se o arquivo de entrada necessita ser
    executado.

    Parâmetros:
    -----------
    pattern: str
        string contendo o formato padrão dos arquivos de saída, porém, sem
        formatação. Ex: '{}_FT{}.png'
    args: list de (arg1, arg2, ...)
        lista de argumentos para formatação do padrão do arquivo de saída. Cada
        elemento da lista é uma tupla contendo os argumentos necessários para
        formatação.

    Retorno:
    --------
    bool:
        booleano indicando se o arquivo de entrada precisa, ou não, ser
        executado.
    """
    logging.info("Verificando se os arquivos já foram processados.")
    execute_file = False
    has_files = []
    for arg in args:
        path = pattern.format(*arg)
        if not os.path.exists(path):
            execute_file = True
        else:
            has_files.append(path)

    if execute_file and has_files:
        pm.cleanupFiles(has_files)

    return execute_file


def applyFourier(patients='all', save_path='.', exec_mode='full'):
    """Aplica a Transformada de Fourier na base de dados CHBMIT.

    script responsável por executar a transformada de fourier sobre a base de
    dados CHBMIT, aos pacientes selecionados. Criando imagens com os espectros,
    salvando em diretórios específicos.

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
    save_path: str
        string contendo o caminho para a pasta em que os resultados serão
        salvos.
    exec_mode: 'full'|'fast'
        opções de execução do script. Se 'full', os arquivos salvos em
        execuções anteriores serãoa removidos e gerando novos resultados. Se
        'fast', os resultados obtidos em execuções anteriores não serão
        calculados novamente.
    """
    logging.info("Iniciando execução do script: Fourier.")

    # extrai os caminhos absolutos dos EDF
    edf_dict = _getCHBMITFilesPath(patients)

    # lista ordenada dos rótulos dos pacientes
    patients_labels = edf_dict.keys()
    patients_labels.sort()

    # cria a estrutura de arquivos para salvar os resultados
    logging.info("Validando/Criando caminhos para salvar resultados.")
    pm.pathStructureValidation(save_path, patients_labels)
    logging.info("Caminhos validados/criados.")

    # padrões para salvar imagens (sinal completo e por bandas)
    band_patterns = ['', '1Delta', '2Theta', '3Alpha', '4Beta', '5Gamma']

    # padão para o nome dos arquivos (base/paciente/arquivo)
    save_file_pat = os.path.join(save_path, "{}", "{}_FT{}.png")

    # limpando arquivos existentes (caso execução completa)
    if exec_mode == 'full':
        logging.info("Limpando Arquivos existentes.")
        files = []
        for plabel in patients_labels:
            for edf_path in edf_dict[plabel]:
                # extrai o nome do arquivo sem a extensão .edf
                edf_label = pm.extractFileLabel(edf_path)
                f = [save_file_pat.format(plabel, edf_label, p)
                     for p in band_patterns]
                files.extend(f)
        pm.cleanupFiles(files)

    logging.debug("Percorrendo lista de pacientes.")
    for plabel in patients_labels:
        logging.info("Executando dados do paciente {}".format(plabel))

        # percorre todos os arquivos .edf
        for edf_path in edf_dict[plabel]:
            print "Executando {}".format(edf_path)

            # extrai o nome do arquivo sem a extensão .edf
            edf_label = pm.extractFileLabel(edf_path)
            logging.debug("Nome do arquivo EDF: {}".format(edf_label))

            # verificando se é necessário executar arquivo
            if exec_mode == 'fast':
                N = len(band_patterns)  # número de padrões
                p_arg1 = [plabel]*N     # primeiro argumento do padrão
                p_arg2 = [edf_label]*N  # segundo argumento do padrão
                p_arg3 = band_patterns  # terceiro argumento do padrão
                p_args = [(i, j, k) for i, j, k in zip(p_arg1, p_arg2, p_arg3)]
                to_exec = _configFastExecution(save_file_pat, p_args)

                if not to_exec:
                    continue

            logging.info("Abrindo arquivo EDF: {}".format(edf_path))
            raw = openEDF(edf_path)

            logging.info("Calculando média dos canais.")
            avg_ch = np.mean(raw._data, axis=0)

            logging.debug("Criando lista (iterador) com canais e média.")
            channel_list = itt.chain(raw._data, [avg_ch])

            logging.info("Calculando Espectro de Potência (Fourier).")
            pspect = []
            for channel in channel_list:
                ft = np.fft.rfft(channel)
                pspect.append(abs(ft)**2)

            freq = np.fft.rfftfreq(len(raw), d=1.0/raw.info['sfreq'])
            logging.debug("Número de Espectros calculados: {}"
                          "".format(len(pspect)))
            logging.debug("Número de Coeficientes nos espectros: {}"
                          "".format(len(pspect[0])))
            logging.debug("Número de frequências calculadas (rfftfreq): {}"
                          "".format(len(freq)))

            logging.info("Calculando parâmetros de plotagem.")

            # número de subplots e lista de rótulos para eixos y
            ylabel_list = raw.ch_names
            ylabel_list.append("AVG")
            xlabel = "Frequências (Hz)"
            title_pat = "Espectro de Potência {}: {}"

            logging.debug("Selecionando Faixas de Frequências.")
            npland = np.logical_and     # shotcut
            e = 0.0000001               # error
            # delta waves [0~4Hz]
            delta = (np.where(npland(freq >= (0-e), freq <= (0+e)))[0][0],
                     np.where(npland(freq >= (4-e), freq <= (4+e)))[0][0])

            # theta waves [4~8Hz]
            theta = (np.where(npland(freq >= (4-e), freq <= (4+e)))[0][0],
                     np.where(npland(freq >= (8-e), freq <= (8+e)))[0][0])

            # alpha waves [8~14Hz]
            alpha = (np.where(npland(freq >= (8-e), freq <= (8+e)))[0][0],
                     np.where(npland(freq >= (14-e), freq <= (14+e)))[0][0])

            # beta waves [14~30Hz]
            beta = (np.where(npland(freq >= (14-e), freq <= (14+e)))[0][0],
                    np.where(npland(freq >= (30-e), freq <= (30+e)))[0][0])

            # gamma waves [>30Hz]
            gamma = (np.where(npland(freq >= (30-e), freq <= (30+e)))[0][0],
                     len(freq))

            wave_band = [(0, len(freq))]    # all freqs
            wave_band.append(delta)
            wave_band.append(theta)
            wave_band.append(alpha)
            wave_band.append(beta)
            wave_band.append(gamma)

            for (ws, wf), pat in zip(wave_band, band_patterns):
                it = [pspect[i][ws:wf] for i in range(len(pspect))]
                img_save_path = save_file_pat.format(plabel, edf_label, pat)

                logging.info("Gerando plot: {}".format(img_save_path))
                plotModels.plotChannels(it, signal_time=freq[ws:wf], dpi=600,
                                        ylabel=ylabel_list, linewidth=0.2,
                                        ytickline_visible=True, xlabel=xlabel,
                                        yticklabel_visible=True, ytick_bins=4,
                                        save_path=img_save_path, figsize=None,
                                        title=title_pat.format(pat, edf_label),
                                        borderwidth=0.2, xtick_size=1.5,
                                        ytick_size=1)

                logging.debug("Imagem salva em {}".format(img_save_path))

            logging.debug("Deletando variáveis.")
            del raw._data
            del raw
            del ft
            del pspect
            del freq
            del avg_ch
            logging.debug("Finalizando execução de {}".format(edf_path))

    logging.info("Verificando existência de arquivos criados.")
    for plabel in patients_labels:
        for edf_path in edf_dict[plabel]:
            edf_label = pm.extractFileLabel(edf_path)
            for pat in band_patterns:
                img_path = save_file_pat.format(plabel, edf_label, pat)
                if os.path.exists(img_path):
                    logging.info("Arquivo OK: {}".format(img_path))
                else:
                    logging.warning("PROBLEMAS AO GERAR IMAGEM. ARQUIVO NÃO "
                                    "ENCONTRADO: {}".format(img_path))
