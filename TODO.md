# TODO:

- [ ] (17) desenvolver script para STFT (com plotagem de 5/10 min)
- [ ] (17) documentar script para STFT
- [ ] (17) desenvolver script para plotar os sinais
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

