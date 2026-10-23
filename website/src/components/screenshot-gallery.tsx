"use client";

import Image from "next/image";
import { Expand, Monitor } from "lucide-react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { asset, screenshots } from "@/lib/site";
import imageMetadata from "../../public/images/image-metadata.json";

export function ScreenshotGallery() {
  return (
    <Tabs defaultValue="recortes" className="gallery-tabs">
      <TabsList className="gallery-tabs-list" aria-label="Telas do aplicativo">
        {screenshots.map((s) => (
          <TabsTrigger value={s.id} key={s.id}>
            {s.label}
          </TabsTrigger>
        ))}
      </TabsList>
      {screenshots.map((s) => (
        <TabsContent value={s.id} key={s.id} className="gallery-panel">
          <div className="gallery-copy">
            <span className="eyebrow">
              <Monitor size={15} /> NO APLICATIVO
            </span>
            <h3>{s.title}</h3>
            <p>{s.text}</p>
            <span className="small-note">
              Captura real do Tibia Enhanced para Windows.
            </span>
          </div>
          <Dialog>
            <DialogTrigger asChild>
              <button
                className="screenshot-button"
                aria-label={`Ampliar captura: ${s.label}`}
              >
                <Image
                  src={asset(`/images/${s.image}`)}
                  alt={`Tela de ${s.label} do Tibia Enhanced`}
                  width={
                    imageMetadata[
                      s.image.replace(".webp", "") as keyof typeof imageMetadata
                    ].width
                  }
                  height={
                    imageMetadata[
                      s.image.replace(".webp", "") as keyof typeof imageMetadata
                    ].height
                  }
                />
                <span className="expand-label">
                  <Expand size={14} /> Ampliar imagem
                </span>
              </button>
            </DialogTrigger>
            <DialogContent className="lightbox">
              <DialogTitle>{s.label} — Tibia Enhanced</DialogTitle>
              <DialogDescription>{s.text}</DialogDescription>
              <Image
                src={asset(`/images/${s.image}`)}
                alt={`Captura ampliada de ${s.label}`}
                width={
                  imageMetadata[
                    s.image.replace(".webp", "") as keyof typeof imageMetadata
                  ].width
                }
                height={
                  imageMetadata[
                    s.image.replace(".webp", "") as keyof typeof imageMetadata
                  ].height
                }
              />
            </DialogContent>
          </Dialog>
        </TabsContent>
      ))}
    </Tabs>
  );
}
