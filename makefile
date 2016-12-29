# project informations
PROJ_DIR = /home/mello/Bancada/codes/Mestrado
PROJ_BIN = bin


# results informations
RESULTS_DIR = /home/mello/Projetos/Mestrado/resultados
INFO_DIR = $(RESULTS_DIR)/info



verify-dataset-file:
	@./$(PROJ_BIN)/datasetFileVerifier --loglevel=info --logfile=$(INFO_DIR)/datasetFileVerifier.log

execute-signal:
	@./$(PROJ_BIN)/execSignal --loglevel=info --logfile=$(INFO_DIR)/execSignal.log --outputdir=$(RESULTS_DIR)

execute-wsignal:
	@./$(PROJ_BIN)/execWindowedSignal --loglevel=info --logfile=$(INFO_DIR)/execWindowedSignal.log --outputdir=$(RESULTS_DIR)

execute-seizure-signal:
	echo "TODO"

execute-signal-statistics:
	echo "TODO"

execute-fourier:
	echo "TODO"
	#@./$(PROJ_BIN)/execFourier --loglevel=info --logfile=$(INFO_DIR)/execFourier.log --outputdir=$(INFO_DIR)

execute-stft:
	echo "TODO"
