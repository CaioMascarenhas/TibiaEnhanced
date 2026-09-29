# Validar captura da janela do Tibia e seleção de região

## Objetivo

Provar que uma região escolhida pelo jogador pode ser capturada continuamente em Python com desempenho aceitável.

## Critérios de aceite

- O jogador escolhe a janela do Tibia e desenha um retângulo sobre ela.
- O protótipo exibe a região capturada ao vivo e mede taxa de quadros e uso de recursos.
- As coordenadas acompanham o movimento e o redimensionamento da janela.
- São testados DPI diferente de 100%, múltiplos monitores e os modos de exibição disponíveis.
- Falhas de captura, janela fechada ou imagem indisponível são mostradas claramente; nenhuma proteção é contornada.
- Um registro técnico compara MSS e `Windows.Graphics.Capture` para orientar a implementação final.

## Dependências

Issue 01.
