# Preparação da distribuição — issue #6

Avaliação em 02/10/2026. A issue continua aberta. O executável e o ZIP portátil foram gerados e passaram nos diagnósticos locais; instalação/desinstalação e a matriz com o cliente real ainda estão pendentes. Consulte [build e resultados](windows-build.md).

## Situação verificada

| Critério da issue | Resultado |
| --- | --- |
| Testes manuais de captura, áudio, suspensão, DPI e monitores | Parcial. Há relatos em `capture-spike.md` e `mirrors.md`, mas falta a matriz final com o executável distribuído. DPI físico acima de 100% e modos de vídeo permanecem pendentes no comentário da issue. |
| Aviso e recuperação quando a origem desaparece | Implementado e validado em testes automatizados e no executável com uma janela sintética em outro processo: minimizar/restaurar, fechar/reabrir, manter preferências e respeitar ocultação voluntária. Ainda requer validação com o cliente real. |
| Instalação, execução e desinstalação | Execução do ZIP validada em Windows 10 x64, incluindo outro caminho com espaço/acento e diretório de trabalho fora do projeto. Definição Inno Setup preparada com ícones; compilação, instalação e desinstalação pendentes porque o compilador não está instalado. |
| Pacote sem segredos e sem envio de dados do jogo | A inspeção de `src/` não encontrou cliente de rede ou upload. Os links externos são abertos pelo usuário. O build verifica a ausência de Git, virtualenv, configurações pessoais, perfis e `.env`; os 37 assets do pacote foram comparados com os originais. Isso não equivale a uma auditoria de dependências ou de tráfego. |
| Revisão das regras atuais da CipSoft | Pendente. O site oficial retornou HTTP 403 nesta consulta. Não foi possível concluir a leitura integral atual nem estabelecer autorização para o espelhamento DWM. |

Os 63 testes automatizados passaram no código final. Donate, cursor medieval e ajustes de portabilidade/recuperação estão no commit `a2259ab`; empacotamento e diagnósticos estão no commit `5f5d38f`. O pacote foi gerado a partir desse último commit com a árvore de código limpa. Os diagnósticos headless e nativo do executável retornaram `frozen: true` e `status: passed`.

## Problemas concretos antes do empacotamento

1. **Sons padrão: corrigido em código e testes.** A exportação usa `sound_asset` para os sons internos, com resolução na instalação atual. A leitura migra caminhos antigos reconhecidos como pertencentes à pasta `tibiaenhanced/audios`. Áudios personalizados mantêm seus caminhos, inclusive quando têm o mesmo nome de um som interno. Foram verificados mudança de instalação, migração de perfil e identificadores inválidos.
2. **Recuperação dos espelhos: corrigida em código e testes.** Interrupções de origem são distinguidas de ocultação voluntária. A verificação ocorre a cada segundo somente enquanto há recortes aguardando. A recuperação preserva janela, região, geometria e aparência, atualiza o HWND e requer vinculação manual quando a identidade é ambígua. A intenção de visibilidade é preservada no perfil durante a espera. O usuário pode cancelar a recuperação; shutdown encerra a verificação.
3. **Build implementado e testado localmente.** Há script/spec de PyInstaller versionados, dependências de build fixadas, ZIP portátil, manifesto com hash/commit e ícone do app incorporado no PE em sete tamanhos. A definição do instalador usa o mesmo ícone para setup, atalhos e desinstalação. Workflow de release e compilação do instalador permanecem pendentes.
4. **Revisão de licenças pendente.** O pacote inclui as licenças dos assets e os avisos encontrados nas distribuições Python/PySide6/shiboken6/mss. Não há licença do projeto na raiz. Escolher a licença do app, conferir a completude dos avisos e a procedência/permissão de imagens e áudios. Ser gratuito não elimina obrigações de redistribuição do Qt/PySide6.

## Caminho proposto

1. Consolidar as mudanças de portabilidade/recuperação já implementadas e as demais mudanças que entrarão na versão.
2. Gerar um build **Windows x64, PyInstaller em modo onedir, sem console**, em ambiente de build separado e com versões registradas/fixadas. Incluir Python, PySide6, plugins usados de Qt/Multimedia, sons, imagens, QR Pix, fontes, SVGs e licenças. O usuário não deve precisar instalar Python.
3. Testar primeiro um **ZIP portátil** da pasta gerada. A recomendação de começar por onedir segue a documentação do PyInstaller: esse modo facilita diagnosticar arquivos e bibliotecas ausentes; onefile adiciona extração temporária a cada execução.
4. Depois dos testes, gerar um **instalador Inno Setup por usuário**, com atalhos e desinstalador. Manter os perfis no diretório de configuração obtido por `QStandardPaths`, fora da pasta de instalação. Atualizações preservam os perfis; desinstalação deve explicar como remover os dados pessoais, se desejado.
5. Preparar versão, notas de lançamento, instruções, arquivos de licença e hashes SHA-256. Testar instalação/atualização/desinstalação em uma máquina ou VM limpa. Publicar os artefatos de um commit/tag identificado quando os critérios estiverem atendidos.

Um certificado de assinatura pode ser avaliado para a distribuição pública; não é necessário para começar a validar o pacote local. Servidor, login e atualizador automático não são necessários para esta primeira versão.

## Matriz de validação do pacote

Registrar versão do Windows, versão do app, monitores/escalas, cenário, resultado e evidência. Os resultados locais do pacote estão em [windows-build.md](windows-build.md); as partes físicas e de instalação abaixo continuam pendentes.

- Windows 11 x64 sem Python instalado; incluir Windows 10 x64 na matriz apenas se for declarado como suportado.
- Abrir sem console; conferir todas as abas, fontes, ícones, cursores, imagens e QR Pix. Validado no pacote local; repetir na máquina limpa.
- MP3 padrão e WAV/MP3 personalizado, teste de som, volume, loop e atalhos com o app em foco.
- Suspender/retomar com timer vencido; alertar uma vez, conforme o comportamento documentado.
- Tibia em janela, sem bordas e tela cheia disponível; minimizar, restaurar, fechar e reabrir.
- Dois ou mais clientes: nunca reassociar silenciosamente a origem errada.
- DPI físico 100%, 125%, 150% e 200%; mover app e espelhos entre monitores com escalas diferentes e coordenadas negativas.
- Mostrar/ocultar, bloquear/desbloquear, opacidade, ajuste de imagem, movimento e redimensionamento dos espelhos.
- Medir CPU/GPU e observar fluidez com 1, 5 e 10 recortes, registrando o hardware. Não apresentar FPS de miniatura como medida da API DWM.
- Reiniciar app, alternar perfis, mover o pacote portátil e atualizar a instalação; manter configurações e sons padrão funcionando. Roundtrip de perfil temporário, sons padrão e mudança de caminho validados; atualização instalada pendente.
- Instalar como usuário comum, usar caminho com espaços/acentos e desinstalar; verificar o tratamento dos perfis.
- Inspecionar o conteúdo distribuído: excluir `.git`, virtualenv de desenvolvimento, configurações pessoais, credenciais, logs e scripts de desenvolvimento. A checagem de conteúdo foi feita no build local; validar funcionamento normal sem conexão externa. O executável oferece diagnóstico opcional com perfil temporário, ativado somente por argumentos específicos.

## Fontes

- [Issue #6](https://github.com/CaioMascarenhas/TibiaEnhanced/issues/6) e [pendências de captura registradas](https://github.com/CaioMascarenhas/TibiaEnhanced/issues/6#issuecomment-5901378983).
- [PyInstaller: modos de empacotamento](https://pyinstaller.org/en/stable/operating-mode.html).
- [Inno Setup](https://jrsoftware.org/isinfo.php).
- [Qt: obrigações das licenças abertas](https://www.qt.io/development/open-source-lgpl-obligations).
- [Regras oficiais do Tibia](https://www.tibia.com/support/?subtopic=tibiarules&rule=3b), cuja leitura integral atual permanece pendente nesta avaliação.
