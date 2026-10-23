# Build para Windows x64

O build usa PyInstaller em modo pasta, com Python e bibliotecas embarcados. O usuário extrai o ZIP inteiro e abre `TibiaEnhanced.exe`; a pasta `_internal` precisa permanecer ao lado dele. A versão atual é `1.0.0`, a primeira versão estável. A publicação no GitHub é manual, após validar os pacotes.

## Gerar

Em Windows x64 com Python 3.11, na raiz do projeto:

```powershell
python -m venv .venv-build
./.venv-build/Scripts/python.exe -m pip install -r packaging/requirements-build.txt
./.venv-build/Scripts/python.exe tools/build_windows.py
```

Saídas:

- `dist/TibiaEnhanced/TibiaEnhanced.exe`: executável de GUI, sem console.
- `dist/TibiaEnhanced-1.0.0-windows-x64-portable.zip`: pasta completa para uso portátil.
- `build/windows-version.iss`: versão gerada de `pyproject.toml`, usada pelo instalador.
- `build/TibiaEnhanced.ico`: ícone gerado do PNG original do projeto em 16, 24, 32, 48, 64, 128 e 256 pixels; reutilizado pelo instalador.
- `build/windows-build.json`: versão do aplicativo, canal beta/estável, versões de ferramentas, commit de origem, estado do código, tamanho, SHA-256 e tamanhos de ícone.

O build verifica x64, subsistema gráfico e correspondência exata dos recursos de ícone do executável com o `.ico` do projeto. Fontes, SVGs, imagens, QR Pix, sons e avisos de bibliotecas entram no pacote. Virtualenv, Git, testes, diagnósticos de desenvolvimento e perfis pessoais não entram.

## Diagnóstico do executável

```powershell
./dist/TibiaEnhanced/TibiaEnhanced.exe --smoke-test-report "$PWD/build/bundle-headless.json" --smoke-test-screenshot "$PWD/build/bundle-headless.png" --headless
./dist/TibiaEnhanced/TibiaEnhanced.exe --smoke-test-report "$PWD/build/bundle-native.json" --smoke-test-screenshot "$PWD/build/bundle-native.png"
```

O relatório contém `frozen: true`, `status: passed` e os resultados individuais. O modo headless verifica interface, fontes, imagens, SVGs, QR, perfil temporário, sons portáveis, clipboard e cursor. O modo nativo também reproduz os MP3 com volume zero e cria uma janela sintética em outro processo para verificar DWM, minimização/restauração, fechamento/reabertura, preservação de preferências e ocultação voluntária. Ele não acessa a janela do Tibia nem os perfis reais do usuário.

Repetir o diagnóstico após extrair o ZIP em outro caminho, incluindo espaços e acentos, e usar um diretório de trabalho fora do projeto. Ainda é necessário testar em uma máquina limpa sem Python e executar a matriz física da issue #6.

## Resultado beta registrado em 13/10/2026

Pacote `0.1.0-beta.1` gerado a partir do commit `2cb6fa606fb584e20678f5d555175db8fc0b29cc`
com alterações locais; o manifesto registra `working_tree_dirty: true` e `channel: beta`.

- Suíte de regressão: **85 testes passaram**.
- Executável congelado: diagnóstico headless com `frozen: true` e `status: passed`.
- Versão textual do recurso PE: `0.1.0-beta.1`; manifesto e ZIP conferidos.
- Integridade do ZIP: todos os arquivos passaram e o executável extraído é idêntico ao gerado.
- Instalador: compilação concluída com Inno Setup 7; instalação/desinstalação não testadas nesta rodada.
- Artefatos locais: ZIP portátil e instalador em `dist`, com hashes em `dist/SHA256SUMS.txt`.

Relatório: `build/beta-headless.json`. Este resultado não substitui os testes pendentes
em máquina limpa, Windows 11, cliente real e diferentes configurações de monitores/DPI.
Na validação local registrada acima, a release ainda não havia sido publicada no GitHub.
Os pacotes não receberam assinatura de código.

## Resultado registrado em 02/10/2026

Pacote 0.1.0 gerado do commit `5f5d38f9ba381c1e355768d407572cba256414b3`, com árvore de código limpa, em Windows 10 x64 (10.0.19045), Python 3.11.9, PyInstaller 6.22.3 e PySide6 6.11.2.

| Verificação | Resultado |
| --- | --- |
| Suíte de regressão | 63 testes passaram. |
| Executável headless | `frozen: true`, `status: passed`; recursos, interface, clipboard, cursor e perfil temporário. |
| ZIP extraído em `build/teste portátil`, executado com diretório de trabalho em `%TEMP%` | `frozen: true`, `status: passed`; ambos os MP3 reproduzidos e DWM validado com fonte sintética externa. |
| Recuperação dos espelhamentos | Minimizar/restaurar e fechar/reabrir passaram; geometria, bloqueio, opacidade, ajuste e ocultação voluntária preservados. |
| Ícone e recursos | PE x64 sem console; sete tamanhos de ícone correspondem exatamente ao `.ico`; 37 assets idênticos aos originais. |
| Inspeção visual | Screenshot nativo da aba Donate conferido; texto de gratuidade/doação voluntária e QR legíveis. |
| Integridade do ZIP | Executável extraído idêntico ao gerado; 248 arquivos, 141.186.365 bytes sem compressão; ZIP com 59.637.776 bytes (56,9 MiB). |

Hashes SHA-256:

```text
TibiaEnhanced.exe
181bfa8fa84456744a0bd3bbecff83b5a104ff2108a45a5a5734b6d8745ec70e

TibiaEnhanced-windows-x64-test.zip
f04e61a01e96d80583c34de43446f30c388583b0050ed5037ada83906dda1d8d
```

Relatórios locais: `build/bundle-final-headless.json`, `build/bundle-final-native.json`, `build/windows-build.json`. Evidência visual: `build/bundle-final-native.png`. Esses arquivos gerados não são versionados.

O host possui Python; executar o binário congelado a partir de outra pasta confirma a portabilidade dos caminhos, mas não substitui o teste em máquina limpa. Windows 11, cliente Tibia real, múltiplos monitores/DPI e instalação/desinstalação continuam pendentes na issue #6.

## Instalador e ícones

`packaging/installer.iss` está preparado para Inno Setup, usando o mesmo ícone em `SetupIconFile`. Atalhos e entrada de desinstalação referenciam o ícone incorporado em `TibiaEnhanced.exe`. A instalação é por usuário, sem exigir administrador, e os perfis ficam fora da pasta instalada.

Após instalar o compilador Inno Setup e gerar o pacote:

```powershell
ISCC.exe packaging/installer.iss
```

### Atualizar o instalador

Depois de alterar o código, execute novamente os dois passos na raiz do projeto:

```powershell
./.venv-build/Scripts/python.exe tools/build_windows.py
& "C:\Program Files\Inno Setup 7\ISCC.exe" packaging/installer.iss
```

O primeiro comando reconstrói o aplicativo, seus recursos e o ZIP. O segundo empacota a pasta
recém-gerada em `dist/TibiaEnhanced-1.0.0-windows-x64-setup.exe`. Alterar o código ou gerar somente o ZIP
não modifica um instalador já criado.

Para atualizar uma instalação existente, feche o aplicativo e execute o novo setup na mesma
pasta de instalação. O `AppId` permanece o mesmo, e os perfis ficam fora dessa pasta. Ainda
não há busca automática de atualizações: o novo setup precisa ser distribuído e executado.
Para mudar a versão, atualize somente `project.version` em `pyproject.toml` antes do build.
O executável, o nome do ZIP e a configuração do instalador usam essa mesma origem.
Os recursos numéricos do Windows usam `1.0.0.0`, e a versão textual usa `1.0.0`.
O histórico acima descreve pacotes anteriores de teste; cada novo build precisa de sua própria validação.

A definição do instalador não equivale a uma instalação/desinstalação validada. Publicação, assinatura, revisão das licenças e regras e testes com o cliente real permanecem etapas separadas.

## Release estável no GitHub

Use a tag `v1.0.0`, o título **Tibia Enhanced 1.0.0**, sem marcar **Pre-release**, e publique como a versão mais recente. O texto está em [releases/1.0.0.md](releases/1.0.0.md).

Gere o executável e o instalador a partir do commit da `main` correspondente à tag. Valide os pacotes e anexe o instalador, o ZIP portátil e `SHA256SUMS.txt` antes de publicar. Preserve releases anteriores no histórico.

### Histórico da release beta

Use a tag `v0.1.0-beta.1`, o título **Tibia Enhanced 0.1.0 Beta 1** e marque **Pre-release**.
Anexe o instalador e o ZIP portátil versionados; não distribua o executável interno isoladamente.
O texto inicial da release está em [releases/0.1.0-beta.1.md](releases/0.1.0-beta.1.md).
Gere hashes SHA-256 dos arquivos finais após qualquer assinatura, antes de anexá-los à release.
Os arquivos ZIP/TAR de código-fonte oferecidos automaticamente pelo GitHub não substituem o pacote portátil.

## Proposta de atualização automática

Ainda não implementada. A primeira etapa recomendada é consultar as Releases em segundo plano,
comparar versões e oferecer **Baixar atualização**, abrindo a página oficial no navegador.
Uma segunda etapa pode baixar o instalador em uma pasta temporária, verificar integridade e
assinatura confiável, salvar as configurações, encerrar o app e executar o setup para atualizar
a mesma instalação. O atualizador deve preservar perfis e nunca encerrar timers sem consentimento.

O canal estável ignora pre-releases; o canal beta aceita betas e versões estáveis mais novas.
A API `releases/latest` não retorna betas: para o canal beta, consulte a lista de releases,
ignore drafts e compare versões semanticamente, sem ordenar as tags como texto.
Pacotes portáteis precisam de um processo externo que aguarde o encerramento, substitua a
pasta inteira (incluindo `_internal`) e permita recuperar a versão anterior se a troca falhar.
Falhas de rede não devem impedir o uso do app. Nenhum token privado deve ser embarcado.

Referências: [API de Releases do GitHub](https://docs.github.com/en/rest/releases/releases)
e [parâmetros do instalador Inno Setup](https://jrsoftware.org/ishelp/topic_setupcmdline.htm).
