# Tibia Enhanced

O frontend do site fica em [`website/`](website/README.md): Next.js, shadcn/ui, capturas reais do app e downloads conectados aos releases do GitHub. O build é estático e não exige backend ou banco de dados.

**Beta · Windows x64 · Gratuito**

Tibia Enhanced é um aplicativo desktop para organizar informações e lembretes durante suas hunts no Tibia. Ele permite espelhar partes da janela do jogo em janelas flutuantes, criar alertas sonoros e usar ferramentas de divisão de loot e EXP Share.

O aplicativo funciona localmente e salva suas configurações por perfil. Não é necessário instalar Python para usar o instalador ou o pacote portátil.

## Download e instalação

Os pacotes publicados ficam nas [Releases do GitHub](https://github.com/CaioMascarenhas/tibiaenhanced/releases). A versão atual do projeto é **0.1.0-beta.1**; no GitHub, versões beta devem estar marcadas como **Pre-release**.

Escolha o formato que preferir:

| Pacote | Como usar |
| --- | --- |
| `TibiaEnhanced-0.1.0-beta.1-windows-x64-setup.exe` | Execute o instalador e abra o aplicativo pelo atalho criado. A instalação é por usuário e não exige administrador. |
| `TibiaEnhanced-0.1.0-beta.1-windows-x64-portable.zip` | Extraia o ZIP inteiro e abra `TibiaEnhanced.exe` dentro da pasta extraída. Mantenha `_internal` ao lado do executável. |

Os nomes acima identificam os pacotes gerados pelo projeto; confira na página de Releases quais versões já foram publicadas. O arquivo **Source code** oferecido pelo GitHub contém o código-fonte, e não o aplicativo pronto para usar.

O alvo de distribuição é Windows 10 (build 19041 ou superior) e Windows 11, em x64. Por ser beta, a compatibilidade com Windows 11, diferentes escalas de tela e múltiplos monitores ainda está em validação. Consulte os [resultados e limitações dos testes](docs/windows-build.md).

## Recortes da janela do jogo

A seção **Recortes** permite manter áreas visíveis do Tibia em janelas flutuantes, por exemplo, para acompanhar informações em outra posição da tela.

1. Abra o Tibia e selecione sua janela na seção **Recortes**.
2. Clique em **Novo recorte**, marque a área desejada e dê um nome.
3. Arraste o espelho para posicioná-lo e use suas bordas para redimensionar.
4. Clique com o botão direito no espelho para ajustar opacidade, proporção, bloqueio de cliques ou visibilidade.

Ao selecionar a área, use a roda do mouse ou os botões de zoom para ampliar a imagem e o botão do meio para mover a área ampliada. O bloqueio permite que os cliques atravessem o espelho; desbloqueie pelo painel quando precisar movê-lo novamente.

Os recortes usam miniaturas **DWM**, exibidas pelo compositor do Windows. Quando a janela de origem é minimizada ou fechada, o aplicativo sinaliza a indisponibilidade e tenta recuperar o espelho ao encontrar uma origem válida. Se houver mais de uma janela possível, use **Vincular** para escolher a correta. Posição, tamanho e preferências são preservados.

## Alertas sonoros

Na seção **Alertas**, os temporizadores padrão **Foods** (1 hora) e **Potions** (10 minutos) ajudam a organizar lembretes. Também é possível criar timers com nome, duração, som e volume próprios.

- Inicie, pause, retome ou reinicie cada temporizador.
- Ative **Loop** para repetir o alerta a cada ciclo.
- Use **Testar som** para conferir o áudio antes da hunt.
- Escolha arquivos `.wav` ou `.mp3` e ajuste os volumes individual e geral.
- Configure uma tecla ou combinação para reiniciar e iniciar um timer. Os atalhos funcionam com a janela do aplicativo em foco.

Os timers são iniciados pelo jogador e não detectam ações do jogo. Ao abrir o aplicativo ou trocar de perfil, eles começam parados. Sons personalizados precisam continuar no caminho escolhido; os sons incluídos no pacote acompanham a instalação.

## Ferramentas para party e hunt

A seção **Tools** reúne:

- **Loot Split:** cole o log completo do Party Hunt Analyzer para calcular a divisão igual de lucro e supplies, com comandos de transferência bancária para copiar. Também mostra lucro por hora e Damage Split quando esses dados estão disponíveis.
- **EXP Share:** informe o level para consultar a faixa de levels compatível. A ferramenta calcula a faixa; as demais condições do shared experience continuam sendo verificadas pelo jogo.
- **Rashid:** veja a cidade do dia considerando o server save. Passe o mouse para consultar direções e a próxima troca, ou clique na cidade para abrir a localização no TibiaMaps pelo navegador.

Os cálculos de loot e EXP Share são locais. Os comandos bancários são apenas exibidos para você copiar e executar. Veja [regras, exemplos e fontes das ferramentas](docs/tools.md).

## Perfis e aparência

Crie perfis pelo seletor na barra superior para manter configurações diferentes, por exemplo, uma por personagem. Recortes, posições, timers, sons, volumes, loops e atalhos são salvos automaticamente no arquivo local `profiles.json`, fora da pasta do aplicativo.

O controle de sol e lua na barra lateral alterna entre os temas claro e escuro. A preferência vale para todos os perfis e é restaurada ao reabrir o aplicativo. Ao fechar a janela principal, você pode encerrar o aplicativo ou minimizá-lo para a bandeja, quando ela estiver disponível no Windows.

## Atualização e remoção

As atualizações são **manuais nesta beta**. Baixe o novo pacote nas Releases e feche o aplicativo antes de atualizar:

- **Instalador:** execute o novo setup na mesma pasta da instalação existente.
- **Portátil:** extraia o novo ZIP em uma pasta separada e abra a nova versão.

Os perfis ficam fora da pasta do aplicativo e são preservados ao substituir o pacote. Para remover a versão instalada, use a desinstalação do Windows; para remover a portátil, feche o aplicativo e exclua a pasta extraída. Isso não apaga os perfis salvos.

## Como o aplicativo interage com o Tibia

Tibia Enhanced usa o Windows para espelhar regiões visíveis da janela. Ele não lê memória ou tráfego do cliente, não injeta código, não envia comandos ao Tibia e não executa ações do jogo automaticamente. Não analisa imagens para identificar eventos do jogo. Os alertas são controlados pelo jogador e as ferramentas trabalham com os dados informados por ele.

O projeto é independente, não é afiliado nem aprovado pela CipSoft. Consulte as [regras oficiais do Tibia](https://www.tibia.com/support/?rule=3b&subtopic=tibiarules) ao avaliar seu uso. Detalhes sobre o espelhamento e os testes realizados estão no [relatório técnico](docs/capture-spike.md).

## Apoiar o projeto

O aplicativo é **100% gratuito**. A seção **Apoiar** oferece contribuição voluntária com Tibia Coins para **Mascarenhas The Great** ou com Pix. O valor é escolhido por quem doa.

## Executar pelo código-fonte

Para desenvolvimento, use Windows e Python 3.11 ou superior. No PowerShell, dentro da pasta do projeto:

```powershell
py -3.11 -m venv .venv
./.venv/Scripts/python.exe -m pip install -e .
./.venv/Scripts/python.exe -m tibiaenhanced
```

Para executar os testes:

```powershell
./.venv/Scripts/python.exe -m unittest discover -s tests -v
```

Para gerar o executável, o ZIP portátil e o instalador, consulte o [guia de build para Windows](docs/windows-build.md).

## Problemas e sugestões

Abra uma [issue](https://github.com/CaioMascarenhas/tibiaenhanced/issues) com a versão utilizada, a versão do Windows e os passos para reproduzir o problema. Quando houver falhas visuais, informe também a escala de tela e a quantidade de monitores.
