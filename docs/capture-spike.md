# Prova de espelhamento da issue #2

## Resultado

O protótipo permite escolher uma janela, arrastar um retângulo sobre uma miniatura ao vivo e abrir um espelho recortado em outra janela. As coordenadas do recorte são relativas à área interna da janela original; o DWM mantém a relação quando ela se move. A aplicação revalida as dimensões a cada meio segundo e encerra o espelho se a janela fechar, minimizar ou ficar menor que o recorte.

O espelho principal usa `DwmRegisterThumbnail` e `DwmUpdateThumbnailProperties` por `ctypes` em Python. Essas APIs exigem uma janela de destino de nível superior, razão pela qual o seletor e a prévia são janelas separadas. A miniatura é composta pelo Windows; Python controla a área de origem e a geometria de destino, mas não recebe os quadros em memória. O painel mostra o uso aproximado de CPU do processo. A taxa real de quadros da miniatura não é exposta pela API DWM; o painel informa essa limitação sem apresentar uma medida falsa.

## Testes locais

| Método | Cliente Tibia | Janela sintética vermelha |
| --- | --- | --- |
| MSS, região do monitor | Preto em modo maximizado e em janela 1100 × 650. | Capturou corretamente em monitores à esquerda e à direita. |
| Windows Graphics Capture | Dez quadros do cliente vieram pretos; em janela menor, somente a moldura apareceu. | Não necessário para o diagnóstico. |
| DXGI Desktop Duplication | Região interna preta no monitor principal com o Tibia em primeiro plano. | Não necessário para o diagnóstico. |
| Miniatura DWM | **O jogador confirmou visualmente o jogo espelhado no monitor.** Capturas de tela da janela espelhada ficaram pretas. | Miniatura vermelha visível e recortável; retângulo de seleção visível em camada transparente. |

`GetWindowDisplayAffinity` informou `WDA_MONITOR` (`0x1`) na janela do Tibia. Isso explica os quadros pretos das APIs de captura testadas. A miniatura DWM é um recurso visual diferente. Capturá-la com MSS deu preto no cliente real, mas o jogador viu o jogo no espelho físico. Portanto o método serve para exibição visual e não para obter pixels em Python.

O teste automatizado de seleção e recorte (`tools/probe_app_dwm.py --synthetic`) confirmou que a implementação produz uma miniatura colorida para janela criada pelo projeto, que o arrasto gera coordenadas válidas e que o espelho exibe a área escolhida. Os testes de geometria MSS verificaram o movimento entre monitores e erro quando a janela fica pequena demais. Todos os monitores locais estavam em escala 100%; uma simulação Qt a 125% passou para MSS, mas o DWM em escala física diferente ainda requer validação. Modo de tela cheia exclusivo também requer validação.

## Limites e conformidade

O projeto não lê memória ou tráfego do Tibia, não injeta código, não instala hooks no processo do jogo e não envia ações ao cliente. Usar uma miniatura DWM da janela protegida pode, contudo, ter implicações nas regras do jogo; a disponibilidade da API do Windows não constitui aprovação da CipSoft. A revisão de regras e uma confirmação com o cliente real continuam necessárias antes de distribuir como solução compatível.

## Reproduzir

Instale o projeto e execute `python -m tibiaenhanced`. Na aba **Recortes**, escolha o Tibia, clique em **Selecionar região**, arraste o retângulo e abra o espelho. Para testar somente a API DWM, execute `python tools/probe_dwm_thumbnail.py --inspect`. Para testar o fluxo com uma janela sintética, execute `python tools/probe_app_dwm.py --synthetic`.

Os diagnósticos de MSS, WGC e DXGI ficam em `tools/`. WGC exige a dependência opcional `pip install -e ".[diagnostics]"`.

## Fontes

- [Microsoft: DwmRegisterThumbnail](https://learn.microsoft.com/en-us/windows/win32/api/dwmapi/nf-dwmapi-dwmregisterthumbnail)
- [Microsoft: DwmUpdateThumbnailProperties](https://learn.microsoft.com/en-us/windows/win32/api/dwmapi/nf-dwmapi-dwmupdatethumbnailproperties)
- [Microsoft: DWM_THUMBNAIL_PROPERTIES](https://learn.microsoft.com/en-us/windows/win32/api/dwmapi/ns-dwmapi-dwm_thumbnail_properties)
- [Microsoft: GetWindowDisplayAffinity](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-getwindowdisplayaffinity)
- [Microsoft: WDA_MONITOR](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setwindowdisplayaffinity)
- [Microsoft: Windows.Graphics.Capture](https://learn.microsoft.com/en-us/windows/uwp/audio-video-camera/screen-capture)
- [CipSoft: Tibia Rules 3b](https://www.tibia.com/support/?rule=3b&subtopic=tibiarules)
