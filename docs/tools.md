# Tools

A seção Tools reúne ferramentas locais de party e hunt. Os logs não são enviados a servidores.

## Loot Split

Cole uma sessão completa do Party Hunt Analyzer e clique em **Dividir loot** (ou Ctrl+Enter).
O painel identifica os participantes, remove o sufixo `(Leader)` dos comandos e valida os valores
de Loot, Supplies e Balance. Logs com totais inconsistentes, jogadores duplicados ou campos
obrigatórios ausentes são recusados para evitar acertos errados.

O saldo de cada jogador é `loot - supplies`. O saldo total é dividido igualmente e as
transferências acertam a diferença entre o saldo atual e a parte devida. Funciona para qualquer
quantidade de jogadores, incluindo hunts com prejuízo. Quando a divisão não resulta em gp inteiros,
a sobra é distribuída na ordem dos participantes no log: os saldos finais diferem em no máximo 1 gp.
O total de gp é preservado, e os comandos do banco usam valores exatos, sem k/kk.

No exemplo usado nos testes, Albus Cruciatus transfere 327375 gp e Blackfang transfere 139014 gp
para Kandin. Cada jogador termina com 611755 gp. A duração informada em `Session` é usada para
calcular o lucro individual por hora; Damage Split aparece quando todos os jogadores têm Damage
e a soma é maior que zero. Modificar o log invalida os resultados antigos.

## EXP Share

A [regra oficial](https://www.tibia.com/support/?entryid=91&subtopic=gethelp) relaciona o menor
level a dois terços do maior; também exige proximidade do líder, participação e ativação do share.
O arredondamento inteiro para baixo, correspondente ao exemplo fornecido e à
[calculadora de referência](https://tibia-wiki.com/15.00/en/ExpShareCalculator), é aplicado ao limite
inferior. O FAQ oficial descreve a proporção, mas não explicita o arredondamento.

Para level `L`: mínimo `floor(2*L/3)` (pelo menos 1), máximo `floor((3*L+2)/2)`.
O máximo é a inversão da condição `floor(2*M/3) <= L`, não apenas `floor(1.5*L)`.
Exemplo: level 200 → 133 a 301. Em parties maiores, a condição deve valer entre o menor e o maior level.

## Rashid

A agenda, direções e coordenadas vêm do [TibiaWiki BR](https://www.tibiawiki.com.br/wiki/Rashid).
O GIF original está incluído no app com a origem registrada em `imgs/RASHID-SOURCE.txt`.
O GIF e a cidade ficam compactos ao lado do título **Tools**. Clicar na cidade abre o TibiaMaps
na coordenada atual; passar o mouse mostra as direções e o horário da próxima troca.

O dia do Tibia muda no server save às **10:00 CET/CEST**, conforme o
[anúncio oficial](https://www.tibia.com/news/?id=1834&subtopic=newsarchive).
O cálculo usa `Europe/Berlin` e os dados IANA embarcados por `tzdata`, inclusive no Windows.
Antes desse horário, o cabeçalho mostra o destino do dia anterior. A próxima troca é exibida no
horário local do computador. O cabeçalho é atualizado ao abrir a seção e a cada 30 segundos enquanto
está visível; o GIF e o timer param ao sair da seção.

## Aparência

O switch compacto no rodapé da navegação mostra apenas **sol e lua**, com indicador deslizante
**amarelo no claro e roxo no escuro**. Funciona com clique ou Espaço quando está em foco.
O tooltip informa o tema que será ativado. A preferência continua salva
localmente e a troca preserva timers, recortes, logs e resultados.
