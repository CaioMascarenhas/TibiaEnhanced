"use client";

import Image from "next/image";
import { useState } from "react";
import {
  Eye,
  LockKeyhole,
  MousePointer2,
  RotateCcw,
  SlidersHorizontal,
} from "lucide-react";
import { Slider } from "@/components/ui/slider";
import { Button } from "@/components/ui/button";
import { asset } from "@/lib/site";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { SpellScene } from "@/components/spell-scene";

export function OverlayDemo() {
  const [example, setExample] = useState("spells");
  const [opacity, setOpacity] = useState(100);
  const [scale, setScale] = useState(100);
  const [locked, setLocked] = useState(true);
  const [visible, setVisible] = useState(true);
  return (
    <Tabs value={example} onValueChange={setExample} className="demo-examples">
      <TabsList
        className="gallery-tabs-list demo-example-tabs"
        aria-label="Exemplo de recortes"
      >
        <TabsTrigger value="spells">Magias no centro</TabsTrigger>
        <TabsTrigger value="vitals">Vida e mana</TabsTrigger>
      </TabsList>
      <TabsContent value={example} className="demo-example-panel">
        <div className="overlay-demo">
          <div
            className={`demo-stage ${example === "spells" ? "spell-stage" : ""}`}
          >
            {example === "spells" ? (
              <SpellScene
                opacity={opacity}
                scale={scale}
                locked={locked}
                visible={visible}
              />
            ) : (
              <>
                <Image
                  className="demo-background"
                  src={asset("/images/tibia-full.webp")}
                  alt="Janela do Tibia capturada pelo projetor do OBS, com barras de vida e mana na parte superior"
                  width={1920}
                  height={1009}
                />
                {visible && (
                  <div
                    className={`demo-overlay ${locked ? "is-locked" : ""}`}
                    style={{
                      opacity: opacity / 100,
                      width: `${(45 * scale) / 100}%`,
                    }}
                  >
                    <div className="overlay-label">
                      <span>
                        <span className="live-dot" /> Vida e mana
                      </span>
                      {locked ? (
                        <LockKeyhole size={12} />
                      ) : (
                        <MousePointer2 size={12} />
                      )}
                    </div>
                    <Image
                      src={asset("/images/tibia-vitals.webp")}
                      alt="Recorte ampliado das barras de vida e mana"
                      width={1118}
                      height={46}
                    />
                    <span className="resize-handle" />
                  </div>
                )}
              </>
            )}
            <span className="demo-caption">
              {example === "spells"
                ? "Três recortes da barra de ações, próximos ao personagem"
                : "Demonstração interativa com uma captura real"}
            </span>
          </div>
          <div className="demo-controls">
            <div className="control-heading">
              <SlidersHorizontal size={18} />
              <span>
                {example === "spells"
                  ? "Magias sempre à vista."
                  : "O recorte é seu."}
              </span>
              <Button
                variant="ghost"
                size="icon"
                aria-label="Restaurar demonstração"
                onClick={() => {
                  setOpacity(100);
                  setScale(100);
                  setLocked(true);
                  setVisible(true);
                }}
              >
                <RotateCcw size={15} />
              </Button>
            </div>
            <div className="demo-sliders">
              <div>
                <label id="opacity-label">
                  Opacidade <span>{opacity}%</span>
                </label>
                <Slider
                  aria-labelledby="opacity-label"
                  value={[opacity]}
                  min={20}
                  max={100}
                  step={1}
                  onValueChange={(v) => setOpacity(v[0])}
                />
              </div>
              <div>
                <label id="scale-label">
                  Tamanho <span>{scale}%</span>
                </label>
                <Slider
                  aria-labelledby="scale-label"
                  value={[scale]}
                  min={70}
                  max={150}
                  step={5}
                  onValueChange={(v) => setScale(v[0])}
                />
              </div>
            </div>
            <div className="demo-toggles">
              <Button
                variant="outline"
                size="sm"
                aria-pressed={locked}
                onClick={() => setLocked(!locked)}
              >
                <LockKeyhole size={14} />
                {locked ? "Bloqueado" : "Bloquear cliques"}
              </Button>
              <Button
                variant="outline"
                size="sm"
                aria-pressed={visible}
                onClick={() => setVisible(!visible)}
              >
                <Eye size={14} />
                {visible ? "Ocultar" : "Mostrar"}
              </Button>
            </div>
            <p className="small-note">
              {example === "spells" &&
                "Os ícones de caveira, espiral e fogo vêm da barra de ações. "}
              No app, arraste para posicionar e use as bordas para
              redimensionar. O bloqueio deixa os cliques passarem para a janela
              abaixo.
            </p>
          </div>
        </div>
      </TabsContent>
    </Tabs>
  );
}
