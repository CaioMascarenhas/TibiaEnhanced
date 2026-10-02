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

A definição do instalador não equivale a uma instalação/desinstalação validada. Publicação, assinatura, revisão das licenças e regras e testes com o cliente real permanecem etapas separadas.
