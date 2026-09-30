# Interface da issue #7

O painel **Recortes** separa três passos: escolher a janela de origem, localizar os recortes agrupados por essa janela e ajustar o recorte selecionado. A árvore usa uma linha de origem e linhas filhas de espelho, com estado visível/oculto e destaque da seleção. O cartão à direita mostra nome, origem, coordenadas, tamanho, estado e apenas as ações do recorte escolhido.

Criar um recorte agora usa um diálogo único: a miniatura ao vivo, seleção por arrasto e campo de nome ficam juntos. O botão de criação só habilita quando a área e o nome são válidos. Os botões têm rótulos, ícones e estados desabilitados conforme a seleção. A aba **Alertas** usa a mesma linguagem visual enquanto sua função é desenvolvida na issue #4.

O tema tem contraste alto, campos e botões padronizados, cartões para agrupar tarefas e rolagem na área de detalhes em janelas menores. A indicação de CPU foi removida do painel. Os espelhos podem ser reduzidos a 24 × 24 pixels, e a faixa de redimensionamento se adapta para preservar espaço de arrasto no centro.

## Verificação

- Prévia visual inspecionada no tamanho padrão de 1100 × 820 e no mínimo de 880 × 720: a seleção permanece visível; no mínimo, os detalhes podem rolar sem cortar os controles.
- Teste de duas miniaturas da mesma origem confirmou que um espelho de 24 × 24 pixels continua mostrando a imagem e pode ser movido pelo centro.
- O diálogo de seleção com nome integrado passou no teste de arrasto com mouse real sobre janela sintética.
- A suíte automatizada valida a árvore com dois recortes e o ciclo de vida dos espelhos.

Persistência dos nomes e posições após reiniciar pertence à issue #5. Validação ampliada de DPI e modos de vídeo pertence à issue #6.
