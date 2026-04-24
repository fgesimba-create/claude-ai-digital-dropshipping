"use client";
import Image from "next/image";
import { useState } from "react";
import type { ProductImage } from "@/lib/api";
import { Zap } from "lucide-react";

interface Props {
  images: ProductImage[];
  name: string;
}

export function ProductGallery({ images, name }: Props) {
  const [selected, setSelected] = useState(0);

  if (!images.length) {
    return (
      <div className="aspect-square bg-dark-700 rounded-2xl flex items-center justify-center">
        <Zap className="w-16 h-16 text-dark-600" />
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="relative aspect-square bg-dark-700 rounded-2xl overflow-hidden">
        <Image
          src={images[selected].url}
          alt={images[selected].alt_text || name}
          fill
          className="object-contain"
          sizes="(max-width: 768px) 100vw, 50vw"
          priority
        />
      </div>
      {images.length > 1 && (
        <div className="flex gap-3 overflow-x-auto pb-1">
          {images.map((img, i) => (
            <button
              key={i}
              onClick={() => setSelected(i)}
              className={`relative w-16 h-16 flex-shrink-0 rounded-lg overflow-hidden border-2 transition-all ${
                selected === i ? "border-brand-500" : "border-dark-600 hover:border-dark-500"
              }`}
            >
              <Image
                src={img.url}
                alt={img.alt_text || `${name} ${i + 1}`}
                fill
                className="object-cover"
                sizes="64px"
              />
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
