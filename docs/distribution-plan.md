# Preparação da distribuição — issue #6

Avaliação em 02/10/2026. A issue continua aberta; ainda não há pacote Windows instalável validado.

## Situação verificada

| Critério da issue | Resultado |
| --- | --- |
| Testes manuais de captura, áudio, suspensão, DPI e monitores | Parcial. Há relatos em `capture-spike.md` e `mirrors.md`, mas falta a matriz final com o executável distribuído. DPI físico acima de 100% e modos de vídeo permanecem pendentes no comentário da issue. |
| Aviso e recuperação quando a origem desaparece | Implementado e validado com testes automatizados: janela reaberta, minimização, região que não cabe, origem ambígua, vinculação manual e cancelamento. Ainda requer validação com o cliente real e com o pacote distribuído. |
| Instalação, execução e desinstalação | Pendente. O README descreve a execução a partir do código e da virtualenv, sem instalador ou guia de desinstalação. |
| Pacote sem segredos e sem envio de dados do jogo | A inspeção de `src/` não encontrou cliente de rede ou upload. Os links externos são abertos pelo usuário. O pacote final ainda precisa ser inspecionado; isso não equivale a uma auditoria de dependências ou de tráfego. |
| Revisão das regras atuais da CipSoft | Pendente. O site oficial retornou HTTP 403 nesta consulta. Não foi possível concluir a leitura integral atual nem estabelecer autorização para o espelhamento DWM. |

Os 63 testes automatizados passaram na árvore de trabalho após os ajustes de sons e recuperação. O commit isolado anterior do fix do cursor na `main` passou em 52 testes. Há alterações locais sem commit, incluindo Donate, cursor medieval e os ajustes de preparação para distribuição; a versão de lançamento precisa partir de um commit que contenha tudo que será distribuído.

## Problemas concretos antes do empacotamento

1. **Sons padrão: corrigido em código e testes.** A exportação usa `sound_asset` para os sons internos, com resolução na instalação atual. A leitura migra caminhos antigos reconhecidos como pertencentes à pasta `tibiaenhanced/audios`. Áudios personalizados mantêm seus caminhos, inclusive quando têm o mesmo nome de um som interno. Foram verificados mudança de instalação, migração de perfil e identificadores inválidos.
2. **Recuperação dos espelhos: corrigida em código e testes.** Interrupções de origem são distinguidas de ocultação voluntária. A verificação ocorre a cada segundo somente enquanto há recortes aguardando. A recuperação preserva janela, região, geometria e aparência, atualiza o HWND e requer vinculação manual quando a identidade é ambígua. A intenção de visibilidade é preservada no perfil durante a espera. O usuário pode cancelar a recuperação; shutdown encerra a verificação.
3. **Build ainda não está definido.** Não há script/spec de PyInstaller, instalador, workflow de release ou versões exatas das dependências de build. `.gitignore` ignora `*.spec`; caso usemos esse formato, o spec do projeto precisa de uma exceção para ser versionado.
4. **Licenças precisam acompanhar o produto.** Há licenças das fontes e dos ícones, mas não há licença do projeto na raiz. Escolher a licença do app, reunir avisos das bibliotecas efetivamente incluídas e conferir a procedência/permissão de imagens e áudios. Ser gratuito não elimina obrigações de redistribuição do Qt/PySide6.

## Caminho proposto

1. Consolidar as mudanças de portabilidade/recuperação já implementadas e as demais mudanças que entrarão na versão.
2. Gerar um build **Windows x64, PyInstaller em modo onedir, sem console**, em ambiente de build separado e com versões registradas/fixadas. Incluir Python, PySide6, plugins usados de Qt/Multimedia, sons, imagens, QR Pix, fontes, SVGs e licenças. O usuário não deve precisar instalar Python.
3. Testar primeiro um **ZIP portátil** da pasta gerada. A recomendação de começar por onedir segue a documentação do PyInstaller: esse modo facilita diagnosticar arquivos e bibliotecas ausentes; onefile adiciona extração temporária a cada execução.
4. Depois dos testes, gerar um **instalador Inno Setup por usuário**, com atalhos e desinstalador. Manter os perfis no diretório de configuração obtido por `QStandardPaths`, fora da pasta de instalação. Atualizações preservam os perfis; desinstalação deve explicar como remover os dados pessoais, se desejado.
5. Preparar versão, notas de lançamento, instruções, arquivos de licença e hashes SHA-256. Testar instalação/atualização/desinstalação em uma máquina ou VM limpa. Publicar os artefatos de um commit/tag identificado quando os critérios estiverem atendidos.

Um certificado de assinatura pode ser avaliado para a distribuição pública; não é necessário para começar a validar o pacote local. Servidor, login e atualizador automático não são necessários para esta primeira versão.

## Matriz de validação do pacote

Registrar versão do Windows, versão do app, monitores/escalas, cenário, resultado e evidência. Os itens abaixo são pendentes até execução e registro no pacote final.

- Windows 11 x64 sem Python instalado; incluir Windows 10 x64 na matriz apenas se for declarado como suportado.
- Abrir sem console; conferir todas as abas, fontes, ícones, cursores, imagens e QR Pix.
- MP3 padrão e WAV/MP3 personalizado, teste de som, volume, loop e atalhos com o app em foco.
- Suspender/retomar com timer vencido; alertar uma vez, conforme o comportamento documentado.
- Tibia em janela, sem bordas e tela cheia disponível; minimizar, restaurar, fechar e reabrir.
- Dois ou mais clientes: nunca reassociar silenciosamente a origem errada.
- DPI físico 100%, 125%, 150% e 200%; mover app e espelhos entre monitores com escalas diferentes e coordenadas negativas.
- Mostrar/ocultar, bloquear/desbloquear, opacidade, ajuste de imagem, movimento e redimensionamento dos espelhos.
- Medir CPU/GPU e observar fluidez com 1, 5 e 10 recortes, registrando o hardware. Não apresentar FPS de miniatura como medida da API DWM.
- Reiniciar app, alternar perfis, mover o pacote portátil e atualizar a instalação; manter configurações e sons padrão funcionando.
- Instalar como usuário comum, usar caminho com espaços/acentos e desinstalar; verificar o tratamento dos perfis.
- Inspecionar o conteúdo distribuído: excluir `.git`, virtualenv de desenvolvimento, configurações pessoais, credenciais, logs e ferramentas de diagnóstico. Validar que o funcionamento normal não depende de conexão externa.

## Fontes

- [Issue #6](https://github.com/CaioMascarenhas/TibiaEnhanced/issues/6) e [pendências de captura registradas](https://github.com/CaioMascarenhas/TibiaEnhanced/issues/6#issuecomment-5901378983).
- [PyInstaller: modos de empacotamento](https://pyinstaller.org/en/stable/operating-mode.html).
- [Inno Setup](https://jrsoftware.org/isinfo.php).
- [Qt: obrigações das licenças abertas](https://www.qt.io/development/open-source-lgpl-obligations).
- [Regras oficiais do Tibia](https://www.tibia.com/support/?subtopic=tibiarules&rule=3b), cuja leitura integral atual permanece pendente nesta avaliação.
