# Redesign visual da issue #9

O aplicativo continua em PySide6. A interface de controle usa uma janela principal de 960 × 680, com mínimo de 800 × 600, barra de título própria e cantos arredondados. Recortes e Alertas compartilham cores, tipografia, ícones e estados de controles. Os espelhos DWM continuam independentes dessa moldura.

## Recursos visuais

- **Exo 900** em títulos e identidade do aplicativo; **Quicksand** em textos e controles. As fontes são carregadas localmente, com Segoe UI como fallback. Licenças em `src/tibiaenhanced/fonts/`.
- Ícones SVG selecionados do **Lucide** em `src/tibiaenhanced/icons/`, com a licença correspondente. O app os renderiza em Qt, sem depender de npm ou de rede durante a execução.
- Paleta escura com superfícies azul-marinho, ação principal em ciano e destaques pontuais em dourado. Cards, campos, botões, abas e sliders usam raios e espaçamentos consistentes.

## Comparação visual

As capturas mostram o conteúdo das janelas, sem a moldura do sistema operacional. No renderizador usado para a captura anterior, Quicksand foi carregada apenas para permitir leitura do texto; a tipografia da versão antiga em execução normal era Segoe UI.

| Tela | Antes | Depois |
| --- | --- | --- |
| Recortes | ![Recortes antes](images/ui-before.png) | ![Recortes depois](images/ui-after.png) |
| Alertas | ![Alertas antes](images/ui-before-alertas.png) | ![Alertas depois](images/ui-after-alertas.png) |

O painel de detalhes de Recortes pode rolar em 800 × 600. Ações de janela (arrastar, redimensionar, minimizar, maximizar, restaurar e fechar) permanecem disponíveis na nova moldura.
