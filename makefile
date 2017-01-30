# project informations
PROJ_DIR = /home/mello/Bancada/codes/Mestrado
PROJ_BIN = bin


# results informations
RESULTS_DIR = /home/mello/Projetos/Mestrado/resultados
INFO_DIR = $(RESULTS_DIR)/info



verify-dataset-file:
	@./$(PROJ_BIN)/datasetFileVerifier --loglevel=info --logfile=$(INFO_DIR)/datasetFileVerifier.log

execute-signal:
	@./$(PROJ_BIN)/execSignal --loglevel=info --logfile=$(INFO_DIR)/execSignal.log --outputdir=$(RESULTS_DIR)/signal

execute-wsignal:
	@./$(PROJ_BIN)/execWindowedSignal --loglevel=info --logfile=$(INFO_DIR)/execWindowedSignal.log --outputdir=$(RESULTS_DIR)/wsignal

execute-seizure-signal:
	@./$(PROJ_BIN)/execSeizureSignal --loglevel=info --logfile=$(INFO_DIR)/execSeizureSignal.log --outputdir=$(RESULTS_DIR)

execute-signal-statistics:
	@./$(PROJ_BIN)/execSignalStatistics --loglevel=info --logfile=$(INFO_DIR)/execSignalStatistics.log --outputdir=$(RESULTS_DIR)

execute-fourier:
	@./$(PROJ_BIN)/execFourier --loglevel=info --logfile=$(INFO_DIR)/execFourier.log --outputdir=$(RESULTS_DIR)

execute-stft:
	@./$(PROJ_BIN)/execSTFT --loglevel=info --logfile=$(INFO_DIR)/execSTFT.log --outputdir=$(RESULTS_DIR)

execute-wt:
	echo "TODO"

execute-rwe:
	echo "TODO"

execute-ws:
	echo "TODO"
