# TODO:

## Plotagens:
- [x] Reestruturar o código em mestrado/xchbmit.py
- [x] Verificar os arquivos das Bases de dados
- [ ] Plotar os sinais (inteiro, em janelas e as crises);
- [ ] Plotar o comportamento da média e do desvio padrão utilizando janelas
  deslizantes;
- [ ] Plotar FT
- [ ] Plotar STFT
- [ ] Plotar Wavelet
- [ ] Plotar RWE (Relative Wavelet Energy)
- [ ] Plotar WS (Wavelet Entropy -- Shannon)
- [ ] Escrever um relatório

## DOING: Plotagem de sinais
- [ ] Plotar o sinal inteiro
- [ ] Plotar o sinal em janelas (default: 10min)
- [ ] Plotar o sinal mostrando o momento da crise, utilizando intervalos antes
  e depois (default: 1min)



## ASAP:
- [ ] Verificar escala de cores na plotagem dos espectros
- [ ] Melhorar a plotagem da barra de escalas
- [x] Testar a função defaultScript
- [x] Documentar a função defaultScript
- [ ] Desenvolver função para plotar STFT
- [ ] Desenvolver função para STFT
- [ ] Inserir anotações
- [ ] Documentar função para STFT
- [ ] Desenvolver script para STFT (com plotagem de 5/10 min)
- [ ] Documentar script para STFT
- [ ] pep8, commit e push
- [ ] Desenvolver função para plotar sinal
- [ ] Documentar função para plotar sinal
- [ ] Desenvolver script para plotar os sinais
- [ ] Documentar script para plotar sinais
- [ ] pep8, commit e push


## ASAP 2
- [ ] (18) desenvolver script para wavelet
- [ ] (19) ler artigo: Wavelet analysis...
- [ ] (19) desenvolver função: relative wavelet energy
- [ ] (19) desenvolver função: wavelet entropy
- [ ] (19) incorporar novas medidas ao script wavelet
- [ ] (19) executar fourier
- [ ] (19) executar STFT
- [ ] (19) executar wavelet (todos)
- [ ] (20) Apresentação em LaTeX para a reunião
- [ ] (20) verificar energia do sinal
- [ ] (21) Quarta (21/12) 10:00 -- Reunião
- [ ] Refatorar applyFourier

## DONE:
- [x] Criar uma função 'esqueleto' para execução dos scripts. A ideia consiste
        em executar o processo de leitura dos arquivos de entrada e verificar
        a existência dos arquivos de saída em uma única função ('esqueleto').
        Esta função recebe uma outra função, a qual irá executar algum tipo de
        operação sobre um único arquivo. Exemplo:

        def esqueleto(params, fun, args):
            # leitura de arquivos utilizando *param*
            # verificar modo de execução
            # ...
            for f in files:
                func(f, *args)
            # ...
            # verificar existência de arquivos de saída

