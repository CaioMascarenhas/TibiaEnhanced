"use client";

import { useEffect, useState } from "react";
import {
  ArrowDownToLine,
  ArrowUpRight,
  Check,
  FileArchive,
  HardDriveDownload,
  LoaderCircle,
  RefreshCw,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { AnimatedCardGrid } from "@/components/animated-card-grid";
import {
  formatSize,
  getPackage,
  parseReleases,
  type Release,
} from "@/lib/releases";
import { RELEASES_API, RELEASES_URL } from "@/lib/site";

export function Downloads() {
  const [releases, setReleases] = useState<Release[]>([]);
  const [selected, setSelected] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [attempt, setAttempt] = useState(0);
  useEffect(() => {
    const controller = new AbortController();
    let disposed = false;
    const timeout = setTimeout(() => controller.abort(), 15000);
    async function load() {
      try {
        const response = await fetch(RELEASES_API, {
          signal: controller.signal,
          headers: { Accept: "application/vnd.github+json" },
        });
        if (!response.ok) throw new Error(`GitHub: ${response.status}`);
        const found = parseReleases(await response.json());
        if (!disposed) {
          setReleases(found);
          setSelected(0);
        }
      } catch {
        if (!disposed)
          setError(
            "Não foi possível consultar as versões agora. Você pode baixar diretamente pelo GitHub ou tentar novamente.",
          );
      } finally {
        clearTimeout(timeout);
        if (!disposed) setLoading(false);
      }
    }
    load();
    return () => {
      disposed = true;
      clearTimeout(timeout);
      controller.abort();
    };
  }, [attempt]);
  const release = releases.find((r) => r.id === selected) || releases[0];
  function retry() {
    setError("");
    setLoading(true);
    setAttempt((v) => v + 1);
  }
  return (
    <div className="downloads-content" aria-live="polite" aria-busy={loading}>
      {loading ? (
        <div className="release-status" role="status">
          <LoaderCircle className="animate-spin" size={23} />
          <p>Consultando as versões publicadas no GitHub…</p>
        </div>
      ) : error ? (
        <div className="release-status">
          <p>{error}</p>
          <Button variant="outline" onClick={retry}>
            <RefreshCw size={15} /> Tentar novamente
          </Button>
        </div>
      ) : !release ? (
        <div className="release-status">
          <p>
            Ainda não há pacotes para Windows publicados. Acompanhe os próximos
            releases no GitHub.
          </p>
        </div>
      ) : (
        <>
          <div className="release-toolbar">
            <div>
              <Badge variant="secondary">
                {release.prerelease
                  ? "Beta · Pré-lançamento"
                  : "Versão estável"}
              </Badge>
              <span className="release-date">
                Publicada em{" "}
                {new Date(release.published_at).toLocaleDateString("pt-BR", {
                  timeZone: "UTC",
                })}
              </span>
            </div>
            <label className="release-select">
              Versão
              <select
                aria-label="Selecionar versão"
                value={release.id}
                onChange={(e) => setSelected(Number(e.target.value))}
              >
                {releases.map((r) => (
                  <option key={r.id} value={r.id}>
                    {r.tag_name}
                    {r.prerelease ? " · Beta" : ""}
                  </option>
                ))}
              </select>
            </label>
          </div>
          <AnimatedCardGrid className="download-grid">
            {(["installer", "portable"] as const).map((format) => {
              const file = getPackage(release, format);
              const installer = format === "installer";
              const Icon = installer ? HardDriveDownload : FileArchive;
              return (
                <article
                  className={`download-card ${installer ? "recommended" : ""}`}
                  key={format}
                >
                  <div className="download-card-top">
                    <Icon size={30} strokeWidth={1.4} />
                    {installer && (
                      <span className="recommend-label">RECOMENDADO</span>
                    )}
                  </div>
                  <h2>{installer ? "Instalador" : "Portátil"}</h2>
                  <p>
                    {installer
                      ? "Instale uma vez. Abra pelo atalho e prepare sua próxima hunt."
                      : "Extraia a pasta e abra o aplicativo. Simples de levar com você."}
                  </p>
                  <ul>
                    <li>
                      <Check size={15} />
                      {installer ? "Atalho no menu Iniciar" : "Sem instalação"}
                    </li>
                    <li>
                      <Check size={15} />
                      {installer
                        ? "Instalação por usuário"
                        : "Extraia o ZIP completo"}
                    </li>
                    <li>
                      <Check size={15} />
                      Sem precisar instalar Python
                    </li>
                  </ul>
                  {file ? (
                    <>
                      <Button
                        asChild
                        className="download-cta"
                        variant={installer ? "default" : "outline"}
                      >
                        <a href={file.browser_download_url}>
                          <ArrowDownToLine size={17} />
                          Baixar {installer ? "instalador" : "ZIP portátil"}
                        </a>
                      </Button>
                      <span className="file-detail">
                        Windows x64 · {formatSize(file.size)}
                        <br />
                        {file.name}
                      </span>
                    </>
                  ) : (
                    <>
                      <Button
                        disabled
                        className="download-cta"
                        variant="outline"
                      >
                        Pacote indisponível nesta versão
                      </Button>
                      <span className="file-detail">
                        Escolha outra versão ou consulte o release.
                      </span>
                    </>
                  )}
                </article>
              );
            })}
          </AnimatedCardGrid>
          <a
            className="text-link release-notes"
            href={release.html_url}
            target="_blank"
            rel="noreferrer"
          >
            Ler notas desta versão <ArrowUpRight size={16} />
          </a>
        </>
      )}
      <div className="github-fallback">
        <p>Todos os arquivos vêm dos releases oficiais do projeto.</p>
        <a
          className="text-link"
          href={RELEASES_URL}
          target="_blank"
          rel="noreferrer"
        >
          Ver todos no GitHub <ArrowUpRight size={16} />
        </a>
      </div>
    </div>
  );
}
