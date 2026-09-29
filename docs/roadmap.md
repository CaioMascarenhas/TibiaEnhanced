# Plano inicial

## Decisões de produto

1. A primeira versão será um aplicativo Windows em Python, com PySide6.
2. Os alertas serão temporizadores iniciados pelo jogador. Detecção automática por imagem não faz parte do escopo inicial.
3. Os espelhos mostrarão pixels da janela escolhida, sem interagir com o cliente do jogo.
4. O aplicativo funcionará localmente, sem conta ou servidor.

## Ordem sugerida

1. Estrutura do aplicativo e janela de controle.
2. Prova de captura com o cliente real e seleção de uma região.
3. Janelas espelhadas e gerenciamento de múltiplos recortes.
4. Temporizadores e reprodução de áudio.
5. Persistência, perfis e recuperação de erros.
6. Testes no Windows, empacotamento e revisão das regras oficiais.

## Pontos para validar no protótipo

- Captura em modo janela e janela sem bordas; imagem preta ou conteúdo protegido deve ser tratado como erro, sem contornar proteções.
- Movimento, redimensionamento e fechamento da janela do Tibia.
- Escala de tela (DPI) e vários monitores.
- Consumo de CPU/GPU com vários recortes.
- Comportamento dos alertas após suspensão e retomada do computador.

## Referências

- [Tibia Rules, 3b](https://www.tibia.com/support/?rule=3b&subtopic=tibiarules)
- [Windows.Graphics.Capture](https://learn.microsoft.com/en-us/windows/uwp/audio-video-camera/screen-capture)
