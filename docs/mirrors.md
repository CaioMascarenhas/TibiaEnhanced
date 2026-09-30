# Espelhos da issue #3

Cada recorte tem nome, coordenadas relativas à janela de origem, modo de ajuste, transparência e uma janela própria sem barra de título. O painel mantém os recortes em memória e oferece criar, renomear, mostrar, ocultar, bloquear, desbloquear e excluir. Posição e tamanho da janela permanecem ao ocultar e mostrar durante a mesma execução; persistência após reiniciar pertence à issue #5.

Os espelhos da mesma janela registram miniaturas DWM com o mesmo `HWND` de origem. O Windows compõe a imagem; o aplicativo não cria capturas separadas em Python. Cada vínculo DWM é registrado quando a janela de espelho abre e removido quando ela fecha. Ocultar ou excluir todos os recortes deixa zero miniaturas ativas.

O modo padrão **Preservar proporção** centraliza a imagem e deixa margens pretas. O modo **Preencher janela** ocupa toda a área e pode distorcer a imagem. O cálculo do destino é atualizado ao redimensionar a janela e usa a escala DPI do monitor.

A imagem pode ser arrastada para mover o espelho. Uma faixa de 9 pixels nas bordas inicia o redimensionamento nativo do Windows. Se a operação nativa não estiver disponível, o Qt aplica a mudança de geometria. O controle de transparência usa a opacidade da janela Qt; 0% de transparência é opaco e 90% mantém o espelho pouco visível, mas recuperável pelo painel.

Bloquear aplica os estilos Windows `WS_EX_NOACTIVATE`, `WS_EX_TRANSPARENT` e `WS_EX_LAYERED` à janela do espelho. Isso impede que ela receba cliques e foco; o jogador pode desbloqueá-la no painel. O espelho permanece sempre visível enquanto aberto. O app não modifica a janela nem o processo do Tibia.

## Validação local

- Duas miniaturas da mesma janela de teste mostraram recortes diferentes: uma vermelha e outra azul.
- Após bloquear uma miniatura, ela continuou vermelha, e um clique físico no centro alcançou o botão da janela de teste abaixo dela.
- Na janela sem barra, um arrasto físico pelo centro moveu aproximadamente 62 × 35 pixels; pela borda, aumentou aproximadamente 53 × 27 pixels.
- A 50% de opacidade, o vermelho se misturou visualmente à janela abaixo; o clique através continuou funcionando ao bloquear.
- Ocultar uma miniatura deixou a outra ativa. Ocultar a última encerrou todos os vínculos DWM.
- Onze testes automatizados passaram, incluindo geometria dos dois modos de ajuste e ciclo de vida de dois recortes da mesma origem.

O script `tools/probe_multi_mirrors.py` reproduz o teste visual sem abrir o Tibia. O cliente real já havia sido validado visualmente na issue #2. Testes finais de DPI físico, modos de vídeo e carga com muitos espelhos continuam na issue #6.

## Fontes

- [Microsoft: miniaturas DWM](https://learn.microsoft.com/en-us/windows/win32/api/dwmapi/nf-dwmapi-dwmregisterthumbnail)
- [Microsoft: estilos estendidos de janela](https://learn.microsoft.com/en-us/windows/win32/winmsg/extended-window-styles)
