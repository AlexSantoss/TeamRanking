import numpy as np
from datetime import datetime
import requests
import re

# Obs: O código possui uma função que cria uma tabela de partidas padrão, usando os dados de league of legends para
# executar. Essa função demora alguns minutos pois precisa acesar muitas paginas (+30). Para que não seja necessária a
# criação de uma nova tabela de jogos e de times a cada execução, estou mandando junto a tabela de jogos padrão.
# Para usar, basta digitar "não" quando for perguntado se quer que o programa pegue uma tabela da internet
# e depois coloque o diretorio onde a tabela está salva no computador junto com o arquivo de times.


def define_var():
    global dicTimes, jogos, resultados, partidas, chutes, numPartidas
    # diretorio = "/home/alhecs/ALA2"
    dicTimes = {}
    jogos = []
    resultados = []
    partidas = []
    chutes = []
    numPartidas = 0


def coleta_info():
    # Função que acessa o site gamesoflegends, pega os dados de todos os campeonatos entre janeiro e maio de 2018 e
    # salva em dois arquivos no diretório escolhido.
    # Um possui o nome Partidas.csv e cada linha dele tem as informações de uma partida. Exemplo de linha:
    # Time A;2;1;Time B;FINAL
    # Essa linha significa que o Time A ganhou de 2x1 do Time B na rodada FINAL
    # O nome do segundo arquivo é Times.csv e contem todos os times do campeonato, um por linha
    # Essa funcao pode ser dispensada se o usuario tiver um arquivo diferente de partidas e de times

    site = "http://www.gamesoflegends.com/tournament/"

    extrai_times_t = re.compile("<h1>Team ranking:</h1>.*?</thead>(.*?)</table>", re.MULTILINE | re.DOTALL)
    extrai_times = re.compile("<tr><td><a href='(.*?)' title='.*?'" +
                              ">(.*?)</a></td>.*?" +
                              "<td class='text-center'>.*?</td><td class='text-center'>.*?" +
                              "</td><td class='text-center'>.*?" +
                              "</td><td class='text-center'>.*?</td></tr>", re.MULTILINE | re.DOTALL)

    extrai_tabela = re.compile("<h1>Last games : </h1>.*?</thead>(.*?)</tr></table>", re.MULTILINE | re.DOTALL)
    extrai_dados = re.compile("href='(.*?)'.*?" +
                              "class='text-right text_.{6,7}'>(.*?)<.*?" +
                              "class='text-center'>(\d) - (\d).*?" +
                              "class='text_.{6,7}'>(.*?)<.*?" +
                              "class='text-center'>(.*?)<.*?" +
                              "class='text-center'>(\d{4}-\d{2}-\d{2})<", re.DOTALL)

    extrai_temps = re.compile("colspan='6'>S8<hr/></td></tr>(.*?)<tr><td ")
    extrai_info_t = re.compile("<tr><td><a href='(.*?)'>(.*?)" +
                               "</a></td><td class='text-center'>(.{2,3})" +
                               "</td><td class='text-center'>(\d*?)" +
                               "</td><td class='text-center'>.*?" +
                               "</td><td>(\d{4}-\d{2}-\d{2})</td><td>(\d{4}-\d{2}-\d{2})</td></tr>")

    html = requests.get(site + "liste.php?region=ALL").text
    fontes = extrai_temps.search(html)
    s8 = extrai_info_t.findall(fontes.group(1))

    fimMSI = datetime.strptime('2018-05-20', '%Y-%m-%d')
    arquivo_times = open(diretorio + "/Times.csv", 'w')
    arquivo_partidas = open(diretorio + "/Partidas.csv", 'w')

    print("---INICIO DA COLETA DE DADOS---")
    for camp in reversed(s8):
        print("\tColetando dados: " + camp[1])
        inicio_camp = datetime.strptime(camp[4], '%Y-%m-%d')
        if inicio_camp > fimMSI:
            continue
        else:
            html = requests.get(site + camp[0][2:]).text
            times = extrai_times.findall(extrai_times_t.search(html).group(1))
            for time in times:
                arquivo_times.write(time[1] + "\n")
            tabela = extrai_tabela.search(html).group(1)
            dados = extrai_dados.findall(tabela)
            for partida in reversed(dados):
                arquivo_partidas.write(';'.join(partida[1:5]))
                if camp[1].startswith('M'):
                    arquivo_partidas.write(";" + partida[5] + "\n")
                else:
                    arquivo_partidas.write(";PRE MSI\n")
    print("\n---FIM---")


def cria_dic_times():
    # Essa função cria um map onde a chave é o nome do time e o valor é um número
    # Esse número serve para indentificar o time, dizendo qual coluna da matriz se refere à esse time

    idx = 0
    tabela_t = open(diretorio + "/Times.csv", 'r')
    for linha in tabela_t.readlines():
        time = linha[:-1]
        if time not in dicTimes:
            dicTimes[time] = idx
            idx += 1


def injeta_rodada(inicio_r, fim_r):
    # Essa função adiciona todos os confrontos de uma rodada na matriz de jogos e seus resultados no vetor de
    # resultados. O time à esquerda do confronto é representado pelo número 1 e o time à direita do confronto é
    # representado pelo numero 1
    # Ex:
    # jogos
    #     A    B   C
    # |   0    1  -1| time b X time c
    # |   1   -1   0| time a x time b
    # |   1    0  -1| time a x time c
    # resultados
    # |   2|  time b ganhou com uma diferenca de 2 pontos
    # |  -1|  time a perdeu com uma diferenca de 1 ponto
    # |   0|  time a empatou com o time c

    rodada = ""
    inicio_r = fim_r
    while fim_r < numPartidas:
        j1, s1, s2, j2, rodada_nova = partidas[fim_r].split(";")
        if rodada == "":
            rodada = rodada_nova
        if rodada != rodada_nova:
            break
        temp = []
        for i in range(len(dicTimes)):
            if i == dicTimes[j1]:
                temp.append(1)
            elif i == dicTimes[j2]:
                temp.append(-1)
            else:
                temp.append(0)
        jogos.append(temp)
        saldo = int(s1) - int(s2)
        resultados.append(saldo)
        # print("Linha adicionada:" + j1 + " " + s1 + "x" + s2 + " " + j2 + "\"" + rodada + "\"")
        fim_r += 1
    return inicio_r, fim_r


def adivinha_proximos(x, inicio_r, fim_r):
    # Ao resolver o sistema linear Ax = b onde A = matriz jogos e b = vetor de resultados, consigo uma solução que é,
    # basicamente, um ranking de times. Cada time possui uma pontuação, onde quanto maior é a pontuação do time,
    # melhor colocado ele está.
    # O Sistema linear retorna um x que minimiza o erro, me retornando assim valores que quase satisfazem todas as
    # linhas da matriz de jogos (os confrontos)

    acerto = erro = 0
    for i in range(inicio_r, numPartidas):
        j1, s1, s2, j2, rodada = partidas[i].split(";")
        if i == inicio_r:
            print(rodada, end='')
            print('\t' + '{:<25}'.format("Time 1") + '{:^15}'.format("Chute") + '{:>25}'.format("Time 2")
                  + ": Resultado")
        if i < fim_r:
            saldo_real = int(s1) - int(s2)
            if saldo_real > 0:
                resultado = "GANHOU DO"
            elif saldo_real < 0:
                resultado = "PERDEU PARA"
            else:
                resultado = "EMPATOU COM O"

            print('\t' + '{:<25}'.format(j1) + '{:^15}'.format(str(chutes[i])) + '{:>25}'.format(j1), end='')
            if resultado == chutes[i]:
                acerto += 1
                print(": Acertei :D")
            else:
                erro += 1
                print(": Errei :(")

        saldo_chute = x[dicTimes[j1]] - x[dicTimes[j2]]
        if np.isclose(saldo_chute, 0.0, atol=1e-6):
            chute = "EMPATOU COM O"
        elif saldo_chute < 0:
            chute = "PERDEU PARA"
        else:
            chute = "GANHOU DO"

        chutes[i] = chute
    return acerto, erro


def main():
    # Função principal que chama todas as outras, incluindo a função np.linalg.lstsq é chamada que resolve um sistema
    # linear usando mínimos quadrados e svd.
    # Essa função é necessária no meu código pois o sistema linear que eu tento resolver, num primeiro momento,
    # geralmente não possui solução. Ao aplicar mínimos quadrados, por possuir colunas linearmente dependentes, o
    # sistema passa de um sem solução para um com infinitas soluções

    global diretorio, partidas, numPartidas, chutes
    define_var()

    print("Escrito por: Alex Santos de Oliveira")
    print("Esse programa usa algebra linear para tentar prever resultados de jogos"
          + "\nVocê deseja que o programa pegue uma tabela de jogos da internet?")
    resposta = input()
    if resposta.lower() == 'sim' or resposta.lower() == 's' or resposta.lower() == 'yes' or resposta.lower() == 'y':
        print("A tabela de jogos padrao contem todos os dados dos campeonatos de League of Legends ate o MSI"
              + "\nDigite um diretorio de sua escolha para que a tabela seja salva. Ex: /home/alhecs/ALA")
        diretorio = input()
        coleta_info()
    else:
        print("Digite o diretorio que contem os arquivos de jogos e de times participantes do campeonato."
              + " Ex: /home/alhecs/ALA\n"
              + "Certifique-se de que o arquivo que contem os jogos "
              + "chama-se 'Partidas.csv' e o arquivo que contem os times chama-se 'Times.csv'")
        diretorio = input()

    cria_dic_times()
    partidas = open(diretorio + "/Partidas.csv", 'r').readlines()
    inicio_r = fim_r = somap = semanas = 0
    numPartidas = len(partidas)
    chutes = [None] * numPartidas
    while fim_r != numPartidas:
        inicio_r, fim_r = injeta_rodada(inicio_r, fim_r)
        x = np.linalg.lstsq(jogos, resultados, rcond=None)[0]
        totais = adivinha_proximos(x, inicio_r, fim_r)
        porcentagem = totais[0] / (totais[0] + totais[1])
        print('\t' + '{:^65}'.format("Porcentagem de acertos na rodada: {:.1%}\n".format(porcentagem)))
        somap += porcentagem
        semanas += 1
    print("Media de Acertos: {:.1%}\n".format(somap/semanas))


main()
