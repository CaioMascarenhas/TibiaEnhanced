# Tibia Enhanced

Aplicativo desktop em Python para espelhar regiões visíveis da janela do Tibia e gerenciar alertas de áudio iniciados pelo jogador.

## Escopo inicial

- Selecionar regiões da janela do jogo e exibi-las em janelas flutuantes, móveis e redimensionáveis.
- Criar temporizadores com nome, duração e som personalizado (`.wav` ou `.mp3`).
- Iniciar, pausar e reiniciar temporizadores pelo aplicativo; atalhos configuráveis podem controlar apenas o aplicativo.
- Salvar localmente os recortes, alertas e posições das janelas.

## Limites do aplicativo

O aplicativo captura apenas a imagem exibida pelo sistema operacional. Ele não lê memória ou tráfego do cliente, não injeta código, não envia comandos ao Tibia e não executa ações do jogo automaticamente. A conformidade deve ser reavaliada conforme as regras oficiais da CipSoft antes da distribuição.

## Arquitetura proposta

- **Interface:** Python e PySide6.
- **Espelhamento:** miniaturas DWM do Windows, registradas e recortadas por Python; resultados dos testes em [docs/capture-spike.md](docs/capture-spike.md).
- **Recortes:** uma captura da janela, compartilhada entre vários espelhos.
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

O aplicativo também instala o comando `tibiaenhanced`. Na aba **Recortes**, escolha a janela do Tibia, clique em **Selecionar região**, arraste um retângulo na imagem e clique em **Iniciar prévia**. A aba **Alertas** será implementada na issue #4.

MSS, Windows Graphics Capture e DXGI retornaram preto para a área do jogo neste cliente. O espelho DWM é exibido diretamente pelo compositor em uma janela do aplicativo; ele não fornece quadros em memória para análise de imagem. Consulte [o relatório técnico](docs/capture-spike.md) para os resultados e limitações dos testes.

Para executar os testes de estrutura e responsividade:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Quando a bandeja do sistema está disponível, fechar a janela a oculta; o menu do ícone oferece **Mostrar**, **Ocultar** e **Sair**. Sem bandeja, fechar a janela encerra o aplicativo.

## Referências

- [Como funciona o TibiaVision](https://tibiavision.com/how-it-works)
- [Regra 3b do Tibia](https://www.tibia.com/support/?rule=3b&subtopic=tibiarules)
- [Captura de tela no Windows](https://learn.microsoft.com/en-us/windows/uwp/audio-video-camera/screen-capture)

Este projeto é independente e não é afiliado à CipSoft.
