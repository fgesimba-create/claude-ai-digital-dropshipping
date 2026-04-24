"use client";
import Image from "next/image";
import Link from "next/link";
import { ShoppingCart, Star, TrendingUp, Zap } from "lucide-react";
import { useCartStore } from "@/lib/store";
import type { Product } from "@/lib/api";
import { useState } from "react";

interface Props {
  product: Product;
}

export function ProductCard({ product }: Props) {
  const addItem = useCartStore((s) => s.addItem);
  const [added, setAdded] = useState(false);

  const primaryImage = product.images.find((i) => i.is_primary) || product.images[0];
  const discount = product.compare_at_price
    ? Math.round((1 - product.sale_price / product.compare_at_price) * 100)
    : null;

  function handleAddToCart(e: React.MouseEvent) {
    e.preventDefault();
    addItem(product);
    setAdded(true);
    setTimeout(() => setAdded(false), 2000);
  }

  return (
    <Link href={`/products/${product.slug}`} className="group block">
      <div className="card hover:border-brand-700/60 transition-all duration-300 hover:shadow-lg hover:shadow-brand-900/20 hover:-translate-y-1">
        {/* Image */}
        <div className="relative aspect-square bg-dark-700 overflow-hidden">
          {primaryImage ? (
            <Image
              src={primaryImage.url}
              alt={primaryImage.alt_text || product.name}
              fill
              className="object-cover group-hover:scale-105 transition-transform duration-500"
              sizes="(max-width: 768px) 50vw, (max-width: 1200px) 33vw, 25vw"
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center">
              <Zap className="w-12 h-12 text-dark-600" />
            </div>
          )}
          {discount && discount > 5 && (
            <span className="discount-badge">-{discount}%</span>
          )}
          {product.is_trending && (
            <span className="trending-badge flex items-center gap-1">
              <TrendingUp className="w-3 h-3" />
              Hot
            </span>
          )}
        </div>

        {/* Content */}
        <div className="p-4">
          {product.category && (
            <p className="text-xs text-brand-400 font-medium mb-1 uppercase tracking-wider">
              {product.category.name}
            </p>
          )}

          <h3 className="font-semibold text-white text-sm leading-snug mb-2 line-clamp-2 group-hover:text-brand-300 transition-colors">
            {product.name}
          </h3>

          {/* Rating */}
          {product.review_count > 0 && (
            <div className="flex items-center gap-1.5 mb-3">
              <div className="flex">
                {Array.from({ length: 5 }).map((_, i) => (
                  <Star
                    key={i}
                    className={`w-3.5 h-3.5 ${i < Math.round(product.rating) ? "text-yellow-400 fill-yellow-400" : "text-dark-600"}`}
                  />
                ))}
              </div>
              <span className="text-xs text-gray-500">({product.review_count})</span>
            </div>
          )}

          {/* Price + CTA */}
          <div className="flex items-center justify-between mt-3">
            <div>
              <span className="price text-lg">${product.sale_price.toFixed(2)}</span>
              {product.compare_at_price && (
                <span className="price-compare ml-2">${product.compare_at_price.toFixed(2)}</span>
              )}
            </div>
            <button
              onClick={handleAddToCart}
              className={`flex items-center gap-1.5 px-3 py-2 rounded-lg text-xs font-semibold transition-all duration-200 active:scale-95 ${
                added
                  ? "bg-green-600 text-white"
                  : "bg-brand-600 hover:bg-brand-500 text-white"
              }`}
            >
              <ShoppingCart className="w-3.5 h-3.5" />
              {added ? "Added!" : "Add"}
            </button>
          </div>

          {/* Shipping */}
          {product.estimated_delivery_days && (
            <p className="text-xs text-gray-600 mt-2 flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-green-500 inline-block" />
              Ships in {product.estimated_delivery_days}
            </p>
          )}
        </div>
      </div>
    </Link>
  );
}

export function ProductCardSkeleton() {
  return (
    <div className="card">
      <div className="aspect-square skeleton" />
      <div className="p-4 space-y-3">
        <div className="skeleton h-3 w-20 rounded" />
        <div className="skeleton h-4 w-full rounded" />
        <div className="skeleton h-4 w-3/4 rounded" />
        <div className="flex justify-between items-center mt-4">
          <div className="skeleton h-6 w-20 rounded" />
          <div className="skeleton h-8 w-16 rounded-lg" />
        </div>
      </div>
    </div>
  );
}
