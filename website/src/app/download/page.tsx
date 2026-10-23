import type { Metadata } from "next";
import { ArrowUpRight, Monitor, ShieldCheck } from "lucide-react";
import { Downloads } from "@/components/downloads";
import { REPOSITORY } from "@/lib/site";

export const metadata: Metadata = {
  title: "Download",
  description:
    "Baixe o instalador ou o ZIP portátil do Tibia Enhanced para Windows x64 diretamente dos releases do GitHub.",
};
export default function DownloadPage() {
  return (
    <main id="conteudo" className="download-page container">
      <div className="download-heading">
        <span className="eyebrow">
          <span className="live-dot" /> PRONTO PARA SUA PRÓXIMA HUNT
        </span>
        <h1>
          Seu setup começa <span>aqui.</span>
        </h1>
        <p>
          Escolha como quer jogar. O Tibia Enhanced é gratuito,
          <br className="desktop-break" /> funciona localmente e não precisa de
          conta.
        </p>
        <div className="requirements">
          <span>
            <Monitor size={15} /> Windows 10 / 11 · x64
          </span>
          <span>
            <ShieldCheck size={15} /> Gratuito
          </span>
        </div>
      </div>
      <Downloads />
      <section className="install-guide">
        <div>
          <span className="eyebrow">DO DOWNLOAD À HUNT</span>
          <h2>Instalou? Agora é com você.</h2>
        </div>
        <ol>
          <li>
            <span>01</span>
            <div>
              <h3>Abra o aplicativo</h3>
              <p>
                Use o instalador ou extraia todo o ZIP. No portátil, mantenha a
                pasta _internal ao lado do executável.
              </p>
            </div>
          </li>
          <li>
            <span>02</span>
            <div>
              <h3>Selecione a janela do Tibia</h3>
              <p>
                Em Recortes, escolha o cliente aberto e crie seu primeiro
                espelho.
              </p>
            </div>
          </li>
          <li>
            <span>03</span>
            <div>
              <h3>Ajuste do seu jeito</h3>
              <p>
                Posição, tamanho, opacidade e alertas. Salve sua organização em
                um perfil.
              </p>
            </div>
          </li>
        </ol>
      </section>
      <div className="compatibility">
        <h3>Sobre esta versão</h3>
        <p>
          Versão 1.0.0. Windows 10 build 19041 ou superior e Windows
          11, em x64, são os alvos de distribuição. Diferentes escalas e
          configurações de monitores continuam em validação.
        </p>
        <a
          className="text-link"
          href={`${REPOSITORY}/blob/main/docs/windows-build.md`}
          target="_blank"
          rel="noreferrer"
        >
          Ver requisitos e limitações <ArrowUpRight size={15} />
        </a>
      </div>
    </main>
  );
}
