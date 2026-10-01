# Tibia Enhanced

Aplicativo desktop em Python para espelhar regiões visíveis da janela do Tibia e gerenciar alertas de áudio iniciados pelo jogador.

## Escopo inicial

- Selecionar regiões da janela do jogo e exibi-las em janelas flutuantes, móveis e redimensionáveis.
- Criar temporizadores com nome, duração e som personalizado (`.wav` ou `.mp3`).
- Iniciar, pausar e reiniciar temporizadores pelo aplicativo; atalhos configuráveis podem controlar apenas o aplicativo.
- Salvar localmente os recortes, alertas e posições das janelas.

## Limites do aplicativo

O aplicativo espelha visualmente a imagem da janela pelo DWM do Windows. Ele não lê memória ou tráfego do cliente, não injeta código, não envia comandos ao Tibia e não executa ações do jogo automaticamente. A conformidade deve ser reavaliada conforme as regras oficiais da CipSoft antes da distribuição.

## Arquitetura proposta

- **Interface:** Python e PySide6.
- **Espelhamento:** miniaturas DWM do Windows, registradas e recortadas por Python; resultados dos testes em [docs/capture-spike.md](docs/capture-spike.md).
- **Recortes:** várias miniaturas DWM podem apontar para a mesma janela de origem; não há cópia de quadros em Python.
- **Alertas:** relógio monotônico e reprodução local de arquivos de áudio.
- **Configurações:** arquivo local versionado por esquema, com migração quando necessário.

O plano de trabalho e os critérios de aceite estão em [docs/roadmap.md](docs/roadmap.md). As propostas de issues estão em [docs/issue-drafts](docs/issue-drafts).

## Executar a base do aplicativo

Requer Windows e Python 3.11 ou superior. No PowerShell, dentro da pasta do projeto:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\python.exe -m tibiaenhanced
```

O aplicativo também instala o comando `tibiaenhanced`. Na aba **Recortes**, escolha a janela do Tibia e clique em **Novo recorte**. No mesmo diálogo, marque a área na imagem e dê um nome. O painel mostra os recortes em cards, com a origem e ações diretas. Clique no lápis para ver detalhes e configurações. Cada espelho abre sem barra de título: arraste a imagem para mover e as bordas para redimensionar. O tamanho mínimo é 24 × 24 pixels. Use **Renomear**, **Mostrar/Ocultar**, **Bloquear/Desbloquear** e **Excluir** no painel. O controle **Transparência** ajusta cada espelho de 0% a 90%. **Preservar proporção** adiciona margens pretas quando necessário; **Preencher janela** estica a imagem. Um espelho bloqueado deixa os cliques atravessarem sua janela; desbloqueie pelo painel.

A janela principal abre em 680 × 460, pode ser reduzida a 560 × 380 e usa uma barra de título própria com controles de minimizar, maximizar e fechar. Arraste a barra para mover a janela e use as bordas para redimensionar. O [experimento visual](docs/modern-ui.md) compara as paletas azul e verde água, com fontes locais Space Grotesk e DM Sans e ícones Lucide.

Na aba **Alertas**, os cards padrão de foods (1 hora) e potions (10 minutos) mostram uma imagem composta dos respectivos itens. Inicie, pause, retome ou reinicie cada temporizador separadamente. O som toca ao fim e pode ser testado pelo botão **Testar som**. Marque **Loop** para tocar novamente a cada ciclo. **Novo timer** cria outro card com nome, duração em segundos, arquivo `.wav` ou `.mp3` e volume próprios. Ao criar ou editar um card, é possível definir uma tecla ou combinação para reiniciar e iniciar a contagem; atalhos repetidos são recusados e funcionam com a janela do aplicativo em foco. O volume geral multiplica o volume individual. A contagem usa relógio monotônico: se o Windows suspender e o prazo passar durante a suspensão, o aviso tocará uma vez quando o aplicativo voltar a processar eventos, e um timer em loop começará um novo ciclo nesse momento. Os temporizadores personalizados ainda não são salvos entre execuções.

MSS, Windows Graphics Capture e DXGI retornaram preto para a área do jogo neste cliente. O espelho DWM é exibido diretamente pelo compositor em uma janela do aplicativo; ele não fornece quadros em memória para análise de imagem. Consulte [o relatório técnico](docs/capture-spike.md) para os resultados e limitações dos testes.

Para executar os testes de estrutura e responsividade:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Quando a bandeja do sistema está disponível, fechar a janela a oculta; o menu do ícone oferece **Mostrar**, **Ocultar** e **Sair**. Sem bandeja, fechar a janela encerra o aplicativo.

Foods e Potions são temporizadores padrão e não podem ser excluídos. O controle **Loop** usa um interruptor arredondado; temporizadores criados pelo usuário podem ser excluídos pelo próprio card.

## Referências

- [Como funciona o TibiaVision](https://tibiavision.com/how-it-works)
- [Regra 3b do Tibia](https://www.tibia.com/support/?rule=3b&subtopic=tibiarules)
- [Captura de tela no Windows](https://learn.microsoft.com/en-us/windows/uwp/audio-video-camera/screen-capture)

Este projeto é independente e não é afiliado à CipSoft.
