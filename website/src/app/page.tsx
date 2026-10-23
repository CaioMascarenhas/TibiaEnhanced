import Link from "next/link";
import Image from "next/image";
import {
  ArrowDown,
  ArrowDownToLine,
  ArrowRight,
  ArrowUpRight,
  BellRing,
  Check,
  Crop,
  CodeXml,
  Layers,
  Monitor,
  MousePointer2,
  SlidersHorizontal,
  Sparkles,
  Swords,
  Wallet,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ScreenshotGallery } from "@/components/screenshot-gallery";
import { OverlayDemo } from "@/components/overlay-demo";
import { FAQ } from "@/components/faq";
import { asset, REPOSITORY } from "@/lib/site";

export default function Home() {
  return (
    <main id="conteudo">
      <section className="hero container">
        <div className="hero-copy">
          <Badge variant="outline" className="hero-badge">
            <span className="live-dot" /> FEITO PARA QUEM JOGA TIBIA{" "}
            <span className="badge-beta">BETA</span>
          </Badge>
          <h1>
            Sua hunt.
            <br />
            <span>Do seu jeito.</span>
          </h1>
          <p>
            As informações que importam, onde você precisa.
            <br className="desktop-break" /> Recortes flutuantes, alertas e
            ferramentas para
            <br className="desktop-break" /> deixar seu setup com a sua cara.
          </p>
          <div className="hero-actions">
            <Button asChild size="lg">
              <Link href="/download/">
                <ArrowDownToLine size={18} /> Baixar para Windows{" "}
                <ArrowUpRight size={17} />
              </Link>
            </Button>
            <a className="hero-secondary" href="#como-funciona">
              Veja como funciona <ArrowDown size={16} />
            </a>
          </div>
          <div className="hero-meta">
            <span>
              <Check size={14} />
              100% gratuito
            </span>
            <span>
              <Monitor size={14} />
              Windows 10 e 11
            </span>
            <span>
              <CodeXml size={14} />
              Código no GitHub
            </span>
          </div>
        </div>
        <div className="hero-art">
          <div className="art-annotation">
            <span className="live-dot" /> SEU JOGO, COM MAIS POSSIBILIDADES
          </div>
          <div className="hero-game">
            <div className="window-top">
              <span className="window-dots">
                <i />
                <i />
                <i />
              </span>
              <span>Tibia · Seu próximo destino</span>
              <span>
                <Monitor size={12} />
              </span>
            </div>
            <Image
              priority
              src={asset("/images/tibia-world.webp")}
              width={1021}
              height={752}
              alt="Mascarenhass no Tibia, em uma ilha com barras de vida e mana ao redor do personagem"
            />
            <div className="game-label">
              <span>CAPTURA REAL DO JOGO</span>
              <span>
                via OBS <span className="live-dot" />
              </span>
            </div>
          </div>
          <div className="floating-vitals">
            <div className="floating-title">
              <Crop size={13} />
              <span>Vida e mana</span>
              <span className="float-dots">···</span>
            </div>
            <Image
              priority
              src={asset("/images/tibia-vitals.webp")}
              width={1199}
              height={48}
              alt="Recorte das barras de vida e mana, separado da área original"
            />
            <span className="resize-corner" />
          </div>
          <div className="floating-skills">
            <div className="floating-title">
              <Layers size={13} />
              Skills <MousePointer2 size={13} />
            </div>
            <Image
              src={asset("/images/tibia-skills.webp")}
              width={178}
              height={184}
              alt="Recorte da janela de Skills do Tibia"
            />
          </div>
          <div className="hero-chip">
            <SlidersHorizontal size={16} />
            <span>Mais foco. Menos procura.</span>
          </div>
        </div>
      </section>
      <div className="feature-strip">
        <div className="container">
          <span>SEU COMPANHEIRO DE HUNT</span>
          <span>
            <Crop size={17} />
            Recortes ao vivo
          </span>
          <span>
            <BellRing size={17} />
            Alertas sonoros
          </span>
          <span>
            <Swords size={17} />
            Ferramentas de party
          </span>
          <span>
            <Layers size={17} />
            Perfis salvos
          </span>
        </div>
      </div>
      <section id="recursos" className="section container">
        <div className="section-heading split-heading">
          <div>
            <span className="eyebrow">UM SETUP QUE ACOMPANHA VOCÊ</span>
            <h2>
              Menos distração.
              <br />
              <span>Mais Tibia.</span>
            </h2>
          </div>
          <p>
            Do primeiro recorte ao acerto de contas da party.
            <br />
            Tudo reunido em um aplicativo simples, feito
            <br className="desktop-break" /> para estar ao seu lado durante a
            hunt.
          </p>
        </div>
        <div className="feature-grid">
          <article className="feature-large">
            <div className="feature-icon">
              <Crop size={23} />
            </div>
            <h3>Seu HUD, no seu lugar.</h3>
            <p>
              Espelhe barras, skills ou qualquer parte da janela. Mova,
              redimensione e ajuste a opacidade para acompanhar tudo sem tirar o
              foco.
            </p>
            <div className="crop-visual">
              <Image
                src={asset("/images/tibia-vitals.webp")}
                alt="Barras de vida e mana selecionadas para criar um recorte"
                width={1118}
                height={46}
              />
              <span className="selection-corner top-left" />
              <span className="selection-corner top-right" />
              <span className="selection-corner bottom-left" />
              <span className="selection-corner bottom-right" />
            </div>
            <div className="feature-tags">
              <span>Redimensionável</span>
              <span>Opacidade ajustável</span>
              <span>Cliques atravessam</span>
            </div>
          </article>
          <article className="feature-small">
            <div className="feature-icon">
              <BellRing size={23} />
            </div>
            <h3>A hora certa de renovar.</h3>
            <p>
              Food, potions e timers personalizados. Escolha seus sons e deixe o
              lembrete com o app.
            </p>
            <div className="timer-preview">
              <span>
                <BellRing size={14} />
                Potions
              </span>
              <strong>10:00</strong>
              <span className="timer-ready">
                <span className="live-dot" />
                Pronto
              </span>
            </div>
          </article>
          <article className="feature-small">
            <div className="feature-icon">
              <Wallet size={23} />
            </div>
            <h3>Party em dia.</h3>
            <p>
              Cole o log, divida supplies e lucro igualmente e copie as
              transferências. Consulte também EXP Share e Rashid.
            </p>
            <div className="party-preview">
              <span>
                <Swords size={15} />
                Loot Split
              </span>
              <span className="party-avatars">
                <i>A</i>
                <i>B</i>
                <i>K</i>
              </span>
              <ArrowUpRight size={18} />
            </div>
          </article>
        </div>
      </section>
      <section id="como-funciona" className="section demo-section">
        <div className="container">
          <div className="section-heading centered">
            <span className="eyebrow">INFORMAÇÃO NO LUGAR CERTO</span>
            <h2>
              Recorte. Posicione. <span>Jogue.</span>
            </h2>
            <p>
              Traga os recortes das magias para perto do personagem. Experimente
              tamanho e transparência no exemplo abaixo.
            </p>
          </div>
          <OverlayDemo />
          <div className="steps-row">
            {[
              [
                "01",
                "Escolha a janela",
                "Abra o Tibia e selecione o cliente no app.",
              ],
              [
                "02",
                "Marque sua área",
                "Crie um recorte da informação que quer acompanhar.",
              ],
              [
                "03",
                "Deixe com a sua cara",
                "Posicione, amplie, ajuste e salve no seu perfil.",
              ],
            ].map(([n, t, d]) => (
              <div key={n}>
                <span className="step-number">{n}</span>
                <div>
                  <h3>{t}</h3>
                  <p>{d}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>
      <section id="galeria" className="section container">
        <div className="section-heading split-heading">
          <div>
            <span className="eyebrow">CONHEÇA POR DENTRO</span>
            <h2>
              Familiar desde
              <br />
              <span>a primeira hunt.</span>
            </h2>
          </div>
          <p>
            Uma interface direta, confortável e organizada.
            <br />
            Veja as telas reais do aplicativo.
          </p>
        </div>
        <ScreenshotGallery />
      </section>
      <section className="local-section container">
        <div className="local-symbol">
          <Image
            src={asset("/images/logo.png")}
            width={108}
            height={108}
            alt="Logo do Tibia Enhanced"
          />
        </div>
        <div>
          <span className="eyebrow">SIMPLES COMO DEVE SER</span>
          <h2>Seu setup fica com você.</h2>
          <p>
            Sem criar conta. Configurações salvas localmente por perfil. Os
            recortes usam o compositor do Windows, e os alertas e cálculos ficam
            sob seu controle.
          </p>
        </div>
        <a
          href={REPOSITORY}
          className="text-link"
          target="_blank"
          rel="noreferrer"
        >
          Conheça o projeto <ArrowUpRight size={17} />
        </a>
      </section>
      <section className="section container faq-section">
        <div className="section-heading">
          <span className="eyebrow">ANTES DA PRÓXIMA HUNT</span>
          <h2>Alguma dúvida?</h2>
          <p>O essencial para começar com tranquilidade.</p>
          <a
            className="text-link"
            href={`${REPOSITORY}/issues`}
            target="_blank"
            rel="noreferrer"
          >
            Converse pelo GitHub <ArrowUpRight size={16} />
          </a>
        </div>
        <FAQ />
      </section>
      <section className="cta-section container">
        <div className="cta-orbit">
          <Sparkles size={25} />
        </div>
        <Badge variant="outline">GRATUITO · WINDOWS x64</Badge>
        <h2>
          Seu próximo upgrade
          <br />é no seu setup.
        </h2>
        <p>Prepare seus recortes, acerte os timers e boa hunt.</p>
        <Button asChild size="lg">
          <Link href="/download/">
            <ArrowDownToLine size={18} /> Baixar Tibia Enhanced{" "}
            <ArrowRight size={18} />
          </Link>
        </Button>
        <span className="small-note">
          Instalador ou portátil. Você escolhe.
        </span>
      </section>
    </main>
  );
}
