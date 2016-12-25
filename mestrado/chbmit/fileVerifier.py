#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import mne

from mestrado.chbmit import utils


def verifyCHBMITFiles():
    """ Verifica quais arquivos EDF da base de dados CHBMIT abrem corretamente.

    Função desenvolvida para verificar quais arquivos da base de dados CHBMIT
    abrem corretamente. Por motivos desconhecidos, alguns arquivos EDF possuem
    canais com rótulos repetidos e incoerentes, causando erros ao lê-los com a
    biblioteca *mne*. Ao verificar quais arquivos podem, ou não, serem abertos,
    imprime em um arquivo de log (se definido) quais arquivos puderam ser
    abertos e quais não foram.
    """
    edf_dict = utils.getCHBMITFilesPath('all')

    patients_labels = edf_dict.keys()
    patients_labels.sort()

    good_data = []
    for plabel in patients_labels:
        msg = "Examinando paciente: {}".format(plabel)
        logging.info(msg)
        print msg

        can_open = True
        for edf_path in edf_dict[plabel]:
            try:
                mne.io.read_raw_edf(edf_path, verbose=False)
            except:
                logging.warning("[Erro ao abrir]: {}".format(edf_path))
                can_open = False

        if can_open:
            good_data.append(plabel)

    logging.info("Pacientes sem arquivos corrompidos.")
    for plabel in good_data:
        logging.info(plabel)
