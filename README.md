# Tibia Enhanced

Aplicativo desktop em Python para espelhar regiões visíveis da janela do Tibia e gerenciar alertas de áudio iniciados pelo jogador.

## Escopo inicial

- Selecionar regiões da janela do jogo e exibi-las em janelas flutuantes, móveis e redimensionáveis.
- Criar temporizadores com nome, duração e som personalizado (`.wav` ou `.mp3`).
- Iniciar, pausar e reiniciar temporizadores pelo aplicativo; atalhos configuráveis podem controlar apenas o aplicativo.
- Salvar localmente os recortes, alertas e posições das janelas.

## Limites do aplicativo

O aplicativo espelha visualmente a imagem da janela pelo DWM do Windows. Ele não lê memória ou tráfego do cliente, não injeta código, não envia comandos ao Tibia e não executa ações do jogo automaticamente. A conformidade deve ser reavaliada conforme as regras oficiais da CipSoft antes da distribuição.

## Arquitetura proposta

- **Interface:** Python e PySide6.
- **Espelhamento:** miniaturas DWM do Windows, registradas e recortadas por Python; resultados dos testes em [docs/capture-spike.md](docs/capture-spike.md).
- **Recortes:** várias miniaturas DWM podem apontar para a mesma janela de origem; não há cópia de quadros em Python.
- **Alertas:** relógio monotônico e reprodução local de arquivos de áudio.
- **Configurações:** arquivo local versionado por esquema para futuras migrações.

O plano de trabalho e os critérios de aceite estão em [docs/roadmap.md](docs/roadmap.md). As propostas de issues estão em [docs/issue-drafts](docs/issue-drafts).

## Executar a base do aplicativo

Requer Windows e Python 3.11 ou superior. No PowerShell, dentro da pasta do projeto:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\python.exe -m tibiaenhanced
```

O aplicativo também instala o comando `tibiaenhanced`. Na aba **Recortes**, escolha a janela do Tibia e clique em **Novo recorte**. No diálogo, use os botões **+** e **−** ou a roda do mouse sobre a imagem para ajustar o zoom; arraste com o botão do meio para mover a área ampliada. Depois marque a área com o botão esquerdo e dê um nome. O painel mostra os recortes em cards, com a origem e ações diretas. Clique no lápis para ver detalhes e configurações. Cada espelho abre sem barra de título: arraste a imagem para mover e as bordas para redimensionar. O botão direito abre um menu para ocultar o espelho, bloquear cliques ou excluir o recorte. O tamanho mínimo é 24 × 24 pixels. Use **Renomear**, **Mostrar/Ocultar**, **Bloquear/Desbloquear** e **Excluir** no painel. O controle **Transparência** ajusta cada espelho de 0% a 90%. **Preservar proporção** adiciona margens pretas quando necessário; **Preencher janela** estica a imagem. Um espelho bloqueado deixa os cliques atravessarem sua janela; desbloqueie pelo painel.

A janela principal abre em 680 × 460, pode ser reduzida a 560 × 380 e usa uma barra de título própria com controles de minimizar, maximizar e fechar. Arraste a barra para mover a janela e use as bordas para redimensionar. O [experimento visual](docs/modern-ui.md) compara as paletas azul e verde água, com fontes locais Space Grotesk e DM Sans e ícones Lucide.

As janelas do aplicativo usam um cursor medieval minimalista: uma ponta de aço com guarda dourada, com brilho sobre controles clicáveis. Os indicadores de edição de texto, seleção de recorte e redimensionamento continuam específicos de cada ação. O cursor acompanha a escala de tela e é aplicado somente dentro do aplicativo.

A aba **Donate** permite apoiar o projeto com Tibia Coins para **Mascarenhas The Great** ou com Pix. O app é **100% gratuito** e a doação é **voluntária**, apenas para quem quiser apoiar o projeto. A aba oferece botões para copiar o personagem, a chave Pix e o código Pix copia e cola, além de um QR Code para ler pelo aplicativo do banco. O valor da contribuição é escolhido por quem doa.

Na aba **Alertas**, os cards padrão de foods (1 hora) e potions (10 minutos) mostram uma imagem composta dos respectivos itens. Inicie, pause, retome ou reinicie cada temporizador separadamente. O som toca ao fim e pode ser testado pelo botão **Testar som**. Marque **Loop** para tocar novamente a cada ciclo. **Novo timer** cria outro card com nome, duração em segundos, arquivo `.wav` ou `.mp3` e volume próprios. Ao criar ou editar um card, é possível definir uma tecla ou combinação para reiniciar e iniciar a contagem; atalhos repetidos são recusados e funcionam com a janela do aplicativo em foco. O volume geral multiplica o volume individual. A contagem usa relógio monotônico: se o Windows suspender e o prazo passar durante a suspensão, o aviso tocará uma vez quando o aplicativo voltar a processar eventos, e um timer em loop começará um novo ciclo nesse momento.

O seletor **Perfil** na barra superior permite criar perfis locais, por exemplo, um por personagem. O botão **+** cria um perfil; o lápis abre as opções para renomear ou excluir o perfil selecionado. A exclusão pede confirmação e mantém pelo menos um perfil disponível. O app salva automaticamente nomes, durações, sons, volumes, loops, atalhos, recortes e posições. O arquivo `profiles.json` fica no diretório de configuração local do aplicativo no Windows. Ao reabrir ou trocar de perfil, os temporizadores voltam parados. Arquivos de áudio personalizados continuam no caminho escolhido; se forem movidos ou excluídos, o app avisa para que você escolha outro. Os recortes procuram a janela pelo título e, se o personagem alterar o título, pelo executável e classe da janela. Quando houver mais de uma janela possível, selecione a correta e clique em **Vincular** na aba Recortes.

Os sons internos são salvos por identificador e resolvidos na pasta atual do aplicativo, para continuar funcionando ao mover ou atualizar a instalação. Caminhos antigos dos sons do pacote são reconhecidos ao carregar o perfil; arquivos personalizados continuam no caminho escolhido pelo usuário.

Se a origem de um espelho visível fechar, minimizar ou ficar menor que o recorte, o app avisa e aguarda sua recuperação. Ele verifica a origem a cada segundo enquanto houver recortes aguardando e retoma quando encontra uma janela válida, preservando posição, tamanho, bloqueio, opacidade e ajuste. Se houver ambiguidade entre janelas, use **Vincular**. O botão de visibilidade permite **Cancelar recuperação**; espelhos ocultados pelo usuário não reaparecem automaticamente.

MSS, Windows Graphics Capture e DXGI retornaram preto para a área do jogo neste cliente. O espelho DWM é exibido diretamente pelo compositor em uma janela do aplicativo; ele não fornece quadros em memória para análise de imagem. Consulte [o relatório técnico](docs/capture-spike.md) para os resultados e limitações dos testes.

Para executar os testes de estrutura e responsividade:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Ao clicar no **X**, escolha **Fechar aplicativo**, **Minimizar para a bandeja** ou **Cancelar**. A opção de minimizar fica disponível quando o Windows oferece a bandeja do sistema. O menu do ícone na bandeja oferece **Mostrar**, **Ocultar** e **Sair**.

Foods e Potions são temporizadores padrão e não podem ser excluídos. O controle **Loop** usa um interruptor arredondado; temporizadores criados pelo usuário podem ser excluídos pelo próprio card.

Nomes de perfis, alertas e recortes têm limite de **24 caracteres**. Nomes maiores em configurações antigas são abreviados com aviso, preservando os demais dados.

Novos recortes usam **Preencher janela** como ajuste padrão. No menu de botão direito do espelho, o slider **Opacidade** ajusta a transparência e **Ajuste da imagem** alterna entre **Preencher janela** e **Preservar proporção**. Essas preferências ficam salvas no perfil.

## Referências

- [Como funciona o TibiaVision](https://tibiavision.com/how-it-works)
- [Regra 3b do Tibia](https://www.tibia.com/support/?rule=3b&subtopic=tibiarules)
- [Captura de tela no Windows](https://learn.microsoft.com/en-us/windows/uwp/audio-video-camera/screen-capture)

Este projeto é independente e não é afiliado à CipSoft.
