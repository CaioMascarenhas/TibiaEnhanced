import Image from "next/image";
import { asset } from "@/lib/site";

const spells = [
  { image: "skull", label: "Magia com ícone de caveira", x: 41.4, y: 35.6 },
  { image: "spiral", label: "Magia com ícone espiralado", x: 59.7, y: 35.6 },
  { image: "fire", label: "Magia com ícone de fogo", x: 50, y: 63.6 },
];

export function SpellScene({
  opacity = 100,
  scale = 100,
  locked = true,
  visible = true,
  priority = false,
}: {
  opacity?: number;
  scale?: number;
  locked?: boolean;
  visible?: boolean;
  priority?: boolean;
}) {
  return (
    <div className="spell-scene">
      <Image
        priority={priority}
        className="spell-background"
        src={asset("/images/tibia-spells-background.webp")}
        alt="Personagem no Tibia, com espaço ao redor para centralizar os recortes de magias"
        width={930}
        height={585}
      />
      {visible &&
        spells.map((spell) => (
          <div
            key={spell.image}
            className={`spell-crop ${locked ? "spell-locked" : "spell-editable"}`}
            style={{
              left: `${spell.x}%`,
              top: `${spell.y}%`,
              width: `${(5.6 * scale) / 100}%`,
              opacity: opacity / 100,
            }}
          >
            <Image
              src={asset(`/images/spell-${spell.image}.webp`)}
              alt={`Recorte da barra de ações: ${spell.label}`}
              width={35}
              height={35}
            />
            {!locked && <span className="resize-handle" />}
          </div>
        ))}
    </div>
  );
}
