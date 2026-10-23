export const REPOSITORY = "https://github.com/CaioMascarenhas/tibiaenhanced";
export const RELEASES_URL = `${REPOSITORY}/releases`;
export const RELEASES_API =
  "https://api.github.com/repos/CaioMascarenhas/tibiaenhanced/releases?per_page=100";
export const asset = (path: string) =>
  `${process.env.NEXT_PUBLIC_BASE_PATH || ""}${path}`;

export const screenshots = [
  {
    id: "recortes",
    label: "Recortes",
    image: "app-recortes.webp",
    title: "Cada informação no seu lugar.",
    text: "Organize seus espelhos, ajuste a opacidade e alterne a visibilidade pelo mesmo painel.",
  },
  {
    id: "alertas",
    label: "Alertas",
    image: "app-alertas.webp",
    title: "Um lembrete na hora certa.",
    text: "Crie timers de food, potions ou o que precisar. Escolha o som, o volume e a repetição.",
  },
  {
    id: "tools",
    label: "Tools",
    image: "app-share.webp",
    title: "Menos contas. Mais hunt.",
    text: "Divida o loot da party, consulte o EXP Share e veja onde está o Rashid.",
  },
  {
    id: "ajustes",
    label: "Ajustes",
    image: "app-editor.webp",
    title: "Ajuste cada detalhe.",
    text: "Controle proporção, transparência, visibilidade e bloqueio de cliques na configuração de cada recorte.",
  },
  {
    id: "aparencia",
    label: "Tema claro",
    image: "app-light.webp",
    title: "Confortável para os seus olhos.",
    text: "Escolha entre claro e escuro. Guarde suas preferências em perfis para cada personagem.",
  },
];
