# TeamRanking
Esse trabalho começa com a pergunta: como rankear times em um campeonato?<br />
Rankear por pontos parece uma boa solução, mas não é a melhor. Esse rankeamento pode favorecer um time que teve uma sequência de confrontos contra times considerados fáceis numa competição.<br />
Outra ideia é analisar seus confrontos anteriores, vendo quais times ele enfrentou e, a partir da pontuação desses outros times, determinar uma pontuação para esse time que está sendo analisado. É a partir dessa ideia que esse trabalho se desenvolve.<br />
É possível representar os times e os jogos de um campeonato através de um grafo, onde os vértices são os times e as arestas são os resultado dos jogos. Uma aresta que vai do time A até o time B, por exemplo, vai ter a aresta com peso igual aos pontos do time A (gols ou qualquer outra métrica) menos os pontos do time B.<br />
Para trazer esse grafo para o mundo de álgebra linear, basta transformar-lo em uma matriz de incidência, onde 1 significa o time de onde está saindo a aresta e -1 o time para o qual a aresta está apontando. Fazendo um exemplo pequeno usando 3 times:<br />
         	
               A    B    C
     	|   0	  1  -1| time b enfrenta o time c
     	|   1    -1   0| time a enfrenta o time b
     	|   1	  0  -1| time a enfrenta o time c

     	|   2|  time b ganhou com uma diferença de 2 pontos
     	|  -1|  time a perdeu com uma diferença de 1 ponto
     	|   0|  time a empatou com o time c

Temos então um sistema linear do tipo Ax = b, onde A é a matriz de incidência e b é o vetor de resultados. Esse sistema também pode ser escrito como:<br />

    	B - C = 2
    	A - B =-1
    	A - C = 0

Pronto, basta resolver esse sistema para descobrir uma solução, que é exatamente o ranking entre esses times. Porém, esse sistema pode não ter solução, sendo necessário assim o uso de métodos mais complexos para ser resolvido.<br />
Para resolver o problema de não ter solução, basta aplicar o método de mínimos quadrados. Esse método projeta o vetor b no espaço gerado pelas colunas matriz, tentando assim diminuir o erro. Logo a solução desse sistema linear será aproximada. Após isso, esbarramos em mais um problema: agora o sistema tem infinitas soluções.<br />
Por ser um sistema que geralmente tem colunas linearmente dependentes, acaba-se tendo infinitas soluções. Ou seja, combinando as colunas da matriz, há infinitos jeitos de se conseguir o vetor b. Para resolver esse problema, usamos o svd (singular-value decomposition). Combinado com o mínimos quadrados, é capaz de se conseguir o vetor de menor norma entre os infinitos possíveis que satisfazem o sistema linear.<br />
Depois de tudo resolvido e com o ranking em mãos, tento dar mais um passo. Tento adivinhar os resultados dos jogos das próximas rodadas de algum campeonato. Para isso, comparo o ranking dos times que estão se enfrentando. Se o ranking de um time A é maior que o do time B, eu chuto que o time A ganhará do B.<br />

Resultados<br />
	Usei, para testar o programa, o campeonato de League of Legends chamado Mid-Season Invitation, campeonato mundial que tem como participantes os melhores times na primeira metade do ano.<br />
	Para tentar aumentar a acurácia, usei os resultados dos campeonatos regionais como se fossem uma pré rodada. Ganhei assim mais dados e algumas relações entre times que participaram desse mundial e que fazem parte da mesma região.<br />
	Resolvendo o sistema linear, consegui uma média de 57.4% de acertos por rodada. A taxa de acerto na rodada variou na maior parte das rodadas entre 50% e 85%, tendo uma descida para 16.7% e um pico em 100% de acertos em uma rodada.<br />

Código<br />
	Para a resolução do sistema linear, eu usei uma função do numpy, a linalg.lstsq, que resolve usando mínimos quadrados e svd, que eu já comentei. Para a coleta de dados, fiz uma função que pega o html de um site. A partir do html, uso regex para extrair os dados que preciso e transformo em uma tabela.<br />
	Fiz algumas alterações no meu código original para tornar-lo mais geral e fácil de se entender. Para usar outros campeonatos, basta ter um arquivo Times.csv contendo todos os times do campeonato e um arquivo Partidas.csv, onde cada linha representa um confronto e que segue o modelo:<br />

       Nome do A;Pontuação do time A;Pontuação do time B;Nome do time B;Semana ou Rodada

Logo, esse código pode ser usado para outros campeonatos. Um exemplo de utilidade é pro futebol, usando os gols como as pontuações dos times. Assim, o codigo se tornou bem mais génerico e com muito mais usos.
