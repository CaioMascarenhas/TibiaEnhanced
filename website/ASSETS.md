# Imagens e identidade visual

Capturas feitas em **22/10/2026**, na sessão Windows do projeto, com autorização do usuário.

- `public/images/tibia-*.webp`: recortes de um quadro original da fonte **Tibao**, no OBS, que alimenta o projetor fornecido pelo usuário. A captura foi salva pela ação nativa **Capturar imagem (fonte)**, com a captura de cursor desativada temporariamente. Assim o ponteiro de controle do computador não entra na imagem. Os três espelhos do usuário foram ocultados durante o print e restaurados com suas opacidades originais.
- `public/images/spell-*.webp`: os três ícones indicados pelo usuário — caveira, espiral e fogo — recortados da barra de ações do mesmo quadro. Os números já fazem parte da imagem original; não foram inventados ou redesenhados.
- `public/images/app-*.webp`: capturas da interface Qt real do projeto em uma sessão de demonstração isolada, renderizadas com `QWidget.grab()` para não incluir o cursor. As telas mostram Recortes, Alertas, Loot Split, EXP Share, configuração e tema claro. Os nomes das três magias e o log de exemplo pertencem à sessão de demonstração; o perfil aberto do usuário não foi alterado para produzir essas imagens. `image-metadata.json` registra as dimensões reais.
- Hero e demonstração interativa: **composições demonstrativas no site**, usando o quadro real e seus recortes. Não são capturas de uma hunt com os controles web sobrepostos pelo aplicativo. O quadro é estático, enquanto os controles de tamanho e opacidade são interativos. O exemplo padrão centraliza as três magias ao redor do personagem, seguindo a referência do usuário; a opção de vida e mana permanece disponível.
- Logo: `src/tibiaenhanced/imgs/iconapp_no_bg.png` do aplicativo, com margem transparente removida e dimensão reduzida.
- Rashid: asset existente no app. A origem está em `src/tibiaenhanced/imgs/RASHID-SOURCE.txt`.
- Fontes DM Sans e Space Grotesk: as mesmas distribuídas com o app. Licenças OFL incluídas em `public/fonts/`.
- Ícones Lucide e componentes shadcn/ui (Radix), com estilos adaptados à paleta do aplicativo.

As imagens foram recortadas e comprimidas em WebP para o site. Nenhuma imagem do jogo foi gerada por IA. Tibia e seus elementos visuais pertencem à CipSoft; o projeto é independente.
