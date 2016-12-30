# TODO:

## Plotagens:
- [x] Reestruturar o código em mestrado/xchbmit.py
- [x] Verificar os arquivos das Bases de dados
- [x] Plotar os sinais (inteiro, em janelas e as crises);
- [x] Plotar o comportamento da média e do desvio padrão utilizando janelas
  deslizantes (para todo o sinal e para os momentos de crise);
- [ ] Plotar FT
- [ ] Plotar STFT
- [ ] Plotar Wavelet
- [ ] Plotar RWE (Relative Wavelet Energy)
- [ ] Plotar WS (Wavelet Entropy -- Shannon)
- [ ] Escrever um relatório

## DOING: Plotagem FT
- [ ] Arrumar script anterior

## ASAP:
- [ ] Verificar escala de cores na plotagem dos espectros



## BUGS - Em algum momento:
### dataset.cfg
- [ ] Mudar o modo como o ConfigParser lê os valores do arquivo de configuração
  para remover '\n' e dividir os valores por ','. Atualmente não está removendo
  as quebras de linha.

### mestrado/chbmit/utils.py
- [ ] mestrado.chbmit.utils._configFastExecution_ e _configFullExecution_ não
  possuem suporte para os casos em que os padrões de plotagem são
  desconhecidos. Uma das possibilidades é utilizar ext_args com o valor None, o
  que causa um erro ao tentar verificar os arquivos criados. Outra forma é
  utilizar orientação a objetos, criando uma classe para o script padrão
  (defaultScript) e outras classes que herdam desta, porém com funções
  específicas (sobreescrita de métodos) para verificar os arquivos de uma forma
  própria.
- [ ] mestrado.chbmit.utils.defaultScript precisa melhorar a parte da função
  que verifica os arquivos já criados. O código está repetido.

### mestrado/chbmit/signal.py
- [ ] mestrado.chbmit.signal.plotCHBMITWindowedSignal: melhorar a forma como o
  caminho para salvar o arquivo é gerado. Foi feita uma gambiarra para
  funcionar e pode ser que em alguns casos aquilo dê erro.

### mestrado/pathManipulation.py
- [ ] mestrado.pathManipulation.extractFileLabel: faz split utilizando '.'
  (ponto), por isso pode dar errado em algum momento. Casos em que o arquivo
  tem outros '.' além do separador com a extensão.

### mestrado/scripts.py
- [ ] mestrado.scripts.execWindowedSignal: inserir suporte para modo de
  execução (exec_mode). Atualmente não está verificando os arquivos gerados.

### mestrado/plotModels.py
- [ ] mestrado.plotModels.defaultPlotStructure: está dando erro ao inserir os
  ticks manualmente, define os rótulos e a posição dos ticks da última área de
  plotagem, porém some com os ticks das outras áreas.
- [ ] mestrado.plotModels.plotSpectrum: axes.flat está dando erro quando tem
  apenas um eixo para plotagem.
