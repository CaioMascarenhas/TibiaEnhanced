"use client";

import { useEffect, useRef, type ReactNode } from "react";
import "./card-motion.css";

export function AnimatedCardGrid({
  children,
  className,
}: {
  children: ReactNode;
  className: string;
}) {
  const grid = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (
      !grid.current ||
      !window.IntersectionObserver ||
      window.matchMedia("(prefers-reduced-motion: reduce)").matches
    ) {
      return;
    }

    const cards = Array.from(grid.current.children) as HTMLElement[];
    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (!entry.isIntersecting) continue;
          (entry.target as HTMLElement).dataset.cardMotion = "visible";
          observer.unobserve(entry.target);
        }
      },
      { threshold: 0.12 },
    );

    for (const card of cards) {
      card.dataset.cardMotion = "pending";
      observer.observe(card);
    }
    return () => {
      observer.disconnect();
      for (const card of cards) delete card.dataset.cardMotion;
    };
  }, []);

  return (
    <div ref={grid} className={`${className} animated-card-grid`}>
      {children}
    </div>
  );
}
