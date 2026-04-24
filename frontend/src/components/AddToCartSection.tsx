"use client";
import { useState } from "react";
import { ShoppingCart, Minus, Plus, Zap } from "lucide-react";
import { useCartStore } from "@/lib/store";
import type { Product } from "@/lib/api";
import Link from "next/link";

interface Props { product: Product }

export function AddToCartSection({ product }: Props) {
  const [qty, setQty] = useState(1);
  const [added, setAdded] = useState(false);
  const addItem = useCartStore((s) => s.addItem);

  function handleAdd() {
    addItem(product, qty);
    setAdded(true);
    setTimeout(() => setAdded(false), 2500);
  }

  return (
    <div className="space-y-4">
      {/* Quantity selector */}
      <div className="flex items-center gap-4">
        <span className="text-sm font-medium text-gray-400">Quantity</span>
        <div className="flex items-center bg-dark-700 rounded-lg border border-dark-600">
          <button
            onClick={() => setQty((q) => Math.max(1, q - 1))}
            className="p-2.5 hover:bg-dark-600 rounded-l-lg transition-colors"
          >
            <Minus className="w-4 h-4 text-gray-400" />
          </button>
          <span className="px-5 font-semibold text-white min-w-[3rem] text-center">{qty}</span>
          <button
            onClick={() => setQty((q) => q + 1)}
            className="p-2.5 hover:bg-dark-600 rounded-r-lg transition-colors"
          >
            <Plus className="w-4 h-4 text-gray-400" />
          </button>
        </div>
      </div>

      {/* Buttons */}
      <div className="flex flex-col sm:flex-row gap-3">
        <button
          onClick={handleAdd}
          className={`flex-1 btn-primary flex items-center justify-center gap-2 text-base py-4 ${
            added ? "bg-green-600 hover:bg-green-600" : ""
          }`}
        >
          <ShoppingCart className="w-5 h-5" />
          {added ? "Added to Cart!" : "Add to Cart"}
        </button>
        <Link
          href="/checkout"
          onClick={() => addItem(product, qty)}
          className="flex-1 border border-brand-500 text-brand-400 hover:bg-brand-900/30 font-semibold px-6 py-4 rounded-lg transition-all text-center flex items-center justify-center gap-2"
        >
          <Zap className="w-5 h-5" />
          Buy Now
        </Link>
      </div>

      {/* Stock indicator */}
      <div className="flex items-center gap-2 text-sm">
        <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
        <span className="text-green-400 font-medium">In Stock</span>
        <span className="text-gray-600">· Ready to ship</span>
      </div>
    </div>
  );
}
