import { createServer } from "node:http";
import { readFile, stat } from "node:fs/promises";
import { resolve, extname, sep } from "node:path";

const root = resolve("out");
const types = { ".html": "text/html; charset=utf-8", ".js": "text/javascript; charset=utf-8", ".css": "text/css; charset=utf-8", ".json": "application/json", ".txt": "text/plain; charset=utf-8", ".webp": "image/webp", ".png": "image/png", ".gif": "image/gif", ".ttf": "font/ttf", ".woff2": "font/woff2", ".ico": "image/x-icon" };
try { await stat(resolve(root, "index.html")); } catch { console.error("Primeiro execute npm run build."); process.exit(1); }

createServer(async (req, res) => {
  if (!["GET", "HEAD"].includes(req.method)) { res.writeHead(405); res.end(); return; }
  try {
    const url = new URL(req.url, "http://127.0.0.1");
    let path = resolve(root, `.${decodeURIComponent(url.pathname)}`);
    if (path !== root && !path.startsWith(root + sep)) { res.writeHead(403); res.end(); return; }
    if ((await stat(path)).isDirectory()) path = resolve(path, "index.html");
    const content = await readFile(path);
    res.writeHead(200, { "Content-Type": types[extname(path)] || "application/octet-stream", "Cache-Control": "no-store" });
    res.end(req.method === "HEAD" ? undefined : content);
  } catch {
    res.writeHead(404, { "Content-Type": "text/html; charset=utf-8" });
    res.end(await readFile(resolve(root, "404.html")).catch(() => "Não encontrado"));
  }
}).listen(3078, "127.0.0.1", () => console.log("Preview estático: http://localhost:3078"));
