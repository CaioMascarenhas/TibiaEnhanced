"use client";

import Link from "next/link";
import Image from "next/image";
import { usePathname } from "next/navigation";
import { useEffect, useState, useSyncExternalStore } from "react";
import {
  ArrowUpRight,
  Download,
  CodeXml,
  Menu,
  Moon,
  Sun,
  X,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Tooltip } from "radix-ui";
import { asset, REPOSITORY } from "@/lib/site";
import "./repository-tooltip.css";

export function Brand() {
  return (
    <Link className="brand" href="/" aria-label="Tibia Enhanced, início">
      <Image src={asset("/images/logo.png")} width={42} height={42} alt="" />
      <span>
        Tibia<span className="brand-light"> Enhanced</span>
      </span>
    </Link>
  );
}

function subscribeTheme(callback: () => void) {
  window.addEventListener("te-theme-change", callback);
  return () => window.removeEventListener("te-theme-change", callback);
}

const getTheme = () => document.documentElement.dataset.theme === "light";

export function Header() {
  const light = useSyncExternalStore(subscribeTheme, getTheme, () => false);
  const [open, setOpen] = useState(false);
  const pathname = usePathname();
  useEffect(() => {
    try {
      const stored = localStorage.getItem("te-site-theme");
      if (stored === "light") document.documentElement.dataset.theme = "light";
      window.dispatchEvent(new Event("te-theme-change"));
    } catch {
      /* The switch still works when storage is unavailable. */
    }
  }, []);
  function toggleTheme() {
    const next = document.documentElement.dataset.theme !== "light";
    document.documentElement.dataset.theme = next ? "light" : "dark";
    try {
      localStorage.setItem("te-site-theme", next ? "light" : "dark");
    } catch {
      /* Optional persistence. */
    }
    window.dispatchEvent(new Event("te-theme-change"));
  }
  return (
    <header className="site-header">
      <div className="container nav-inner">
        <Brand />
        <nav
          className={`nav-links ${open ? "is-open" : ""}`}
          aria-label="Navegação principal"
        >
          <a href={asset("/#recursos")} onClick={() => setOpen(false)}>
            Recursos
          </a>
          <a href={asset("/#como-funciona")} onClick={() => setOpen(false)}>
            Como funciona
          </a>
          <a href={asset("/#galeria")} onClick={() => setOpen(false)}>
            O aplicativo
          </a>
          <Link
            href="/download/"
            className={pathname.startsWith("/download") ? "active-link" : ""}
            onClick={() => setOpen(false)}
          >
            Downloads
          </Link>
        </nav>
        <div className="nav-actions">
          <Tooltip.Provider delayDuration={200}>
            <Tooltip.Root>
              <Tooltip.Trigger asChild>
                <a
                  className="icon-link github-nav"
                  href={REPOSITORY}
                  target="_blank"
                  rel="noreferrer"
                  aria-label="Repositório do GitHub"
                >
                  <CodeXml size={19} />
                </a>
              </Tooltip.Trigger>
              <Tooltip.Portal>
                <Tooltip.Content
                  className="repository-tooltip"
                  side="bottom"
                  sideOffset={12}
                  collisionPadding={16}
                >
                  <span className="repository-tooltip-icon" aria-hidden="true">
                    <CodeXml size={19} />
                  </span>
                  <span className="repository-tooltip-copy">
                    <strong>Repositório do GitHub</strong>
                    <span>Explore o código do projeto</span>
                  </span>
                  <ArrowUpRight size={14} aria-hidden="true" />
                  <Tooltip.Arrow className="repository-tooltip-arrow" width={12} height={6} />
                </Tooltip.Content>
              </Tooltip.Portal>
            </Tooltip.Root>
          </Tooltip.Provider>
          <button
            className="theme-switch"
            onClick={toggleTheme}
            aria-label="Alternar tema claro e escuro"
            aria-pressed={light}
          >
            <Sun size={15} />
            <Moon size={15} />
          </button>
          <Button asChild className="nav-download">
            <Link href="/download/">
              <Download size={15} /> Baixar grátis
            </Link>
          </Button>
          <button
            className="mobile-menu icon-link"
            onClick={() => setOpen(!open)}
            aria-expanded={open}
            aria-label={open ? "Fechar menu" : "Abrir menu"}
          >
            {open ? <X /> : <Menu />}
          </button>
        </div>
      </div>
    </header>
  );
}

export function Footer() {
  return (
    <footer className="site-footer container">
      <div className="footer-main">
        <div>
          <Brand />
          <p>
            Feito por um jogador.
            <br />
            Para quem vive a próxima hunt.
          </p>
        </div>
        <div className="footer-links">
          <Link href="/download/">
            Downloads <ArrowUpRight size={14} />
          </Link>
          <a href={REPOSITORY} target="_blank" rel="noreferrer">
            Código no GitHub <ArrowUpRight size={14} />
          </a>
          <a href={`${REPOSITORY}/issues`} target="_blank" rel="noreferrer">
            Reportar um problema <ArrowUpRight size={14} />
          </a>
        </div>
      </div>
      <div className="footer-bottom">
        <span>
          © {new Date().getFullYear()} Tibia Enhanced · Feito por Mascarenhas
        </span>
        <span>
          Projeto independente, sem afiliação ou aprovação da CipSoft. Tibia é
          marca da CipSoft.
        </span>
      </div>
    </footer>
  );
}
