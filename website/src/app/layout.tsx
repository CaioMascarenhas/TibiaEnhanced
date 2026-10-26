import type { Metadata } from "next";
import Script from "next/script";
import "./globals.css";
import { Header, Footer } from "@/components/site-shell";
export const metadata: Metadata = {
  title: {
    default: "Tibia Enhanced — Sua hunt, do seu jeito.",
    template: "%s | Tibia Enhanced",
  },
  description:
    "Recortes flutuantes, alertas sonoros e ferramentas para sua party. Conheça o Tibia Enhanced, gratuito para Windows.",
  icons: { icon: `${process.env.NEXT_PUBLIC_BASE_PATH || ""}/images/logo.png` },
  openGraph: {
    title: "Tibia Enhanced",
    description:
      "Sua hunt, do seu jeito. Recortes, alertas e ferramentas para Tibia.",
    locale: "pt_BR",
    type: "website",
  },
};
export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="pt-BR" suppressHydrationWarning>
      <head>
        <script
          async
          src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-7308349546540862"
          crossOrigin="anonymous"
        />
      </head>
      <body>
        <a href="#conteudo" className="skip-link">
          Pular para o conteúdo
        </a>
        <Header />
        {children}
        <Footer />
        <Script
          src="https://www.googletagmanager.com/gtag/js?id=G-RHFRDGDCN1"
          strategy="afterInteractive"
        />
        <Script id="google-analytics" strategy="afterInteractive">
          {`
            window.dataLayer = window.dataLayer || [];
            function gtag(){dataLayer.push(arguments);}
            gtag('js', new Date());
            gtag('config', 'G-RHFRDGDCN1');
          `}
        </Script>
      </body>
    </html>
  );
}
