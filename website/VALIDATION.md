# Validação — 22/10/2026

Atualização das imagens: três magias indicadas pelo usuário (caveira, espiral e fogo) centralizadas ao redor do personagem. Alternância entre esse exemplo e vida/mana verificada no navegador; três recortes e ausência de excesso de largura conferidos em desktop e em 390 × 844. Capturas do jogo refeitas pela ação nativa do OBS e telas Qt renderizadas sem cursor. Os espelhos e a configuração original de captura de cursor do OBS foram restaurados. Build e lint passaram após a atualização.

- Build de produção e exportação estática das páginas `/` e `/download/` concluídos.
- ESLint e TypeScript sem erros.
- 4 testes de releases passaram: ordenação e betas, drafts/arquivos-fonte, URLs de outro repositório e pacote ausente.
- Consulta real no navegador identificou `v0.1.0-beta.1`, com instalador e ZIP portátil, data e tamanhos vindos do GitHub.
- Revisão visual em Chrome, desktop e viewport móvel de 390 × 844. Sem excesso de largura no build final.
- Switch claro/escuro e persistência após recarregar, menu móvel, troca de abas, lightbox e fechamento com Escape verificados.
- Demonstração: opacidade 20%, tamanho 150%, bloquear, ocultar e restaurar verificados no navegador.
- `npm audit --omit=dev`: nenhuma vulnerabilidade conhecida nas dependências de produção na data da validação.
- A auditoria completa ainda aponta 5 avisos em dependências transitivas **de desenvolvimento** do ESLint (`braces` → `micromatch` → `fast-glob` → plugin/config Next). O fix automático propõe um downgrade incompatível do ESLint config para Next 14, então não foi aplicado. Essas dependências não fazem parte dos arquivos estáticos publicados.

O estado de erro de rede da página de downloads está implementado com timeout, nova tentativa e link permanente para Releases. A consulta real e a seleção de pacotes foram verificadas; não foi simulada uma queda da API no navegador.
