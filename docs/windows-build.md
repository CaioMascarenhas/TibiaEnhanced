# Build de teste para Windows x64

O build usa PyInstaller em modo pasta, com Python e bibliotecas embarcados. O usuário extrai o ZIP inteiro e abre `TibiaEnhanced.exe`; a pasta `_internal` precisa permanecer ao lado dele. A primeira versão é um pacote de validação, sem publicação automática.

## Gerar

Em Windows x64 com Python 3.11, na raiz do projeto:

```powershell
python -m venv .venv-build
./.venv-build/Scripts/python.exe -m pip install -r packaging/requirements-build.txt
./.venv-build/Scripts/python.exe tools/build_windows.py
```

Saídas:

- `dist/TibiaEnhanced/TibiaEnhanced.exe`: executável de GUI, sem console.
- `dist/TibiaEnhanced-windows-x64-test.zip`: pasta completa para teste em outra instalação.
- `build/TibiaEnhanced.ico`: ícone gerado do PNG original do projeto em 16, 24, 32, 48, 64, 128 e 256 pixels; reutilizado pelo instalador.
- `build/windows-build.json`: versões de ferramentas, commit de origem, estado do código, tamanho, SHA-256 e tamanhos de ícone.

O build verifica x64, subsistema gráfico e correspondência exata dos recursos de ícone do executável com o `.ico` do projeto. Fontes, SVGs, imagens, QR Pix, sons e avisos de bibliotecas entram no pacote. Virtualenv, Git, testes, diagnósticos de desenvolvimento e perfis pessoais não entram.

## Diagnóstico do executável

```powershell
./dist/TibiaEnhanced/TibiaEnhanced.exe --smoke-test-report "$PWD/build/bundle-headless.json" --smoke-test-screenshot "$PWD/build/bundle-headless.png" --headless
./dist/TibiaEnhanced/TibiaEnhanced.exe --smoke-test-report "$PWD/build/bundle-native.json" --smoke-test-screenshot "$PWD/build/bundle-native.png"
```

O relatório contém `frozen: true`, `status: passed` e os resultados individuais. O modo headless verifica interface, fontes, imagens, SVGs, QR, perfil temporário, sons portáveis, clipboard e cursor. O modo nativo também reproduz os MP3 com volume zero e cria uma janela sintética em outro processo para verificar DWM, minimização/restauração, fechamento/reabertura, preservação de preferências e ocultação voluntária. Ele não acessa a janela do Tibia nem os perfis reais do usuário.

Repetir o diagnóstico após extrair o ZIP em outro caminho, incluindo espaços e acentos, e usar um diretório de trabalho fora do projeto. Ainda é necessário testar em uma máquina limpa sem Python e executar a matriz física da issue #6.

## Instalador e ícones

`packaging/installer.iss` está preparado para Inno Setup, usando o mesmo ícone em `SetupIconFile`. Atalhos e entrada de desinstalação referenciam o ícone incorporado em `TibiaEnhanced.exe`. A instalação é por usuário, sem exigir administrador, e os perfis ficam fora da pasta instalada.

Após instalar o compilador Inno Setup e gerar o pacote:

```powershell
ISCC.exe packaging/installer.iss
```

A definição do instalador não equivale a uma instalação/desinstalação validada. Publicação, assinatura, revisão das licenças e regras e testes com o cliente real permanecem etapas separadas.
