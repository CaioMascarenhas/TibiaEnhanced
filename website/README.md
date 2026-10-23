# Site do Tibia Enhanced

Frontend em **Next.js App Router, TypeScript, Tailwind CSS e shadcn/ui com Radix**. Paleta, fontes e logo vêm do aplicativo desktop. Páginas `/` e `/download/`, galeria com ampliação, demonstração de recortes, FAQ e temas claro/escuro.

## Rodar localmente

Use Node.js **22.18 ou superior** (Node 24 recomendado) e npm.

```powershell
cd website
npm ci
npm run dev -- --port 3077
```

Abra http://localhost:3077. O site é independente do ambiente Python do aplicativo.

## Validar e gerar o site

```powershell
npm test
npm run lint
npm run typecheck
npm run build
npm run preview
```

O build gera `out/` com HTML, CSS, JavaScript, fontes e imagens. `preview` serve o resultado em http://localhost:3078. **Não exige servidor Next.js em produção**, banco, API própria, chave secreta ou conta de usuário.

## Downloads do GitHub

O navegador consulta a API pública de releases ao abrir `/download/`. São consideradas as últimas 100 releases públicas com instalador ou ZIP portátil compatível com Windows x64, ordenadas pela data de publicação. Versões beta são incluídas e identificadas; o endpoint `/releases/latest` não é usado, pois ignora pré-lançamentos.

- O seletor permite escolher uma release anterior.
- Nome, tamanho, data, tag e URL vêm da resposta real do GitHub.
- Os botões usam `browser_download_url` diretamente. Os arquivos não passam pelo site.
- Apenas URLs HTTPS do repositório esperado são aceitas.
- Drafts, arquivos de código-fonte e pacotes ausentes não viram botões de download.
- Se a API falhar, atingir rate limit ou não responder em 15 segundos, a página oferece nova tentativa e link para Releases. Sem releases válidas, mostra um estado vazio.
- Nada depende de rebuild do site ao publicar uma nova versão do app.

Para atualizar os downloads, publique uma release no GitHub e anexe os pacotes com os padrões usados hoje: `TibiaEnhanced-<versão>-windows-x64-setup.exe` e `TibiaEnhanced-<versão>-windows-x64-portable.zip`. Os arquivos `Source code` não substituem esses pacotes. Consulte `src/lib/site.ts` para o repositório e `src/lib/releases.ts` para validação e seleção.

## Hospedar

### Docker na VPS

O GitHub Actions gera e publica `ghcr.io/caiomascarenhas/tibiaenhanced-web:latest` quando há alterações em `website/` na `main`. A imagem suporta Linux amd64 e arm64 e também recebe uma tag imutável `sha-<commit>`. PRs validam o build sem publicar; a execução manual fica na aba Actions.

Com Docker Engine e Docker Compose instalados, execute dentro de `website/` na VPS:

```bash
docker compose pull
docker compose up -d
```

O Compose baixa a imagem pronta. A VPS não compila o projeto nem precisa de Node ou Python. O contêiner serve o site estático com Nginx na porta interna **8787**, com verificação de saúde; não publica portas no host.

No **Nginx Proxy Manager**, adicione um Proxy Host:

- Scheme: `http`.
- Forward Hostname / IP: `tibiaenhanced-web`.
- Forward Port: `8787`.
- Configure seu domínio e certificado SSL no próprio Nginx Proxy Manager.

Os dois serviços precisam estar conectados à mesma rede Docker externa. Por padrão, o Compose usa `proxy`. Se sua rede tiver outro nome:

```bash
PROXY_NETWORK=nome-da-rede docker compose up -d
```

Para manter esse ajuste entre comandos, configure `PROXY_NETWORK` em um arquivo `.env` ao lado do Compose. O site deve ser servido na raiz do domínio.

O GHCR cria novos pacotes como privados por padrão. Para download sem autenticação, o proprietário pode tornar o pacote público nas configurações de Packages do GitHub. Se permanecer privado, faça `docker login ghcr.io -u SEU_USUARIO` na VPS e informe um token com `read:packages` no campo de senha. O workflow usa o `GITHUB_TOKEN` fornecido pelo GitHub para publicar, sem segredo adicional no repositório.

Para atualizar a VPS depois de uma publicação bem-sucedida da Action:

```bash
docker compose pull
docker compose up -d
docker compose ps
```

Use `git pull --ff-only` quando precisar atualizar o próprio Compose. Para fixar ou voltar a uma imagem específica, configure `IMAGE_TAG=sha-<commit>` no `.env`. Os downloads continuam sendo consultados diretamente no GitHub pelo navegador, sem reconstruir a imagem a cada release do aplicativo.

### Outros hosts estáticos

Publique o **conteúdo** de `website/out/` em um host estático. Também funciona com hosts que executam `npm ci && npm run build` na pasta `website` e publicam `out`.

Para GitHub Pages em um subdiretório, configure o caminho **durante o build**:

```powershell
$env:NEXT_PUBLIC_BASE_PATH='/tibiaenhanced'
npm run build
```

Use o nome e a capitalização reais do caminho público. Para domínio próprio na raiz, deixe `NEXT_PUBLIC_BASE_PATH` vazio. Links, imagens e fontes suportam esse caminho. A hospedagem precisa permitir chamadas do navegador a `https://api.github.com`.

## Capturas e acessibilidade

Veja [ASSETS.md](ASSETS.md) para a origem das imagens. A galeria contém capturas reais do app; o hero e a demonstração são composições explícitas com recortes do quadro real do OBS. Os controles Radix suportam teclado, o lightbox fecha com Escape, há link para pular o cabeçalho e as animações respeitam `prefers-reduced-motion`.

Testes da integração de releases: `tests/releases.test.mjs`. As capturas de QA e os pacotes para revisão ficam fora do código versionado, em `build/site-captures/` e `output/` na raiz do repositório.
