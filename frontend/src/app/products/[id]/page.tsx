export const dynamic = "force-dynamic";
import { getProduct } from "@/lib/api";
import { notFound } from "next/navigation";
import { AddToCartSection } from "@/components/AddToCartSection";
import { ProductGallery } from "@/components/ProductGallery";
import { Star, Truck, Shield, RotateCcw, TrendingUp } from "lucide-react";
import type { Metadata } from "next";

interface Props {
  params: Promise<{ id: string }>;
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { id } = await params;
  const product = await getProduct(id).catch(() => null);
  if (!product) return { title: "Product Not Found" };
  return {
    title: product.meta_title || product.name,
    description: product.meta_description || product.short_description,
  };
}

export default async function ProductPage({ params }: Props) {
  const { id } = await params;
  const product = await getProduct(id).catch(() => null);
  if (!product) notFound();

  const discount = product.compare_at_price
    ? Math.round((1 - product.sale_price / product.compare_at_price) * 100)
    : null;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
        {/* Gallery */}
        <ProductGallery images={product.images} name={product.name} />

        {/* Details */}
        <div className="space-y-6">
          {/* Category + badges */}
          <div className="flex items-center gap-3 flex-wrap">
            {product.category && (
              <span className="badge-blue">{product.category.name}</span>
            )}
            {product.is_trending && (
              <span className="badge-orange flex items-center gap-1">
                <TrendingUp className="w-3 h-3" />
                Trending
              </span>
            )}
          </div>

          {/* Name */}
          <h1 className="text-3xl font-bold text-white leading-tight">{product.name}</h1>

          {/* Rating */}
          {product.review_count > 0 && (
            <div className="flex items-center gap-3">
              <div className="flex">
                {Array.from({ length: 5 }).map((_, i) => (
                  <Star
                    key={i}
                    className={`w-5 h-5 ${i < Math.round(product.rating) ? "text-yellow-400 fill-yellow-400" : "text-dark-600"}`}
                  />
                ))}
              </div>
              <span className="text-gray-400 text-sm">
                {product.rating.toFixed(1)} ({product.review_count} reviews)
              </span>
              <span className="text-gray-600 text-sm">·</span>
              <span className="text-gray-400 text-sm">{product.sale_count} sold</span>
            </div>
          )}

          {/* Price */}
          <div className="flex items-baseline gap-4">
            <span className="text-4xl font-extrabold text-white">
              ${product.sale_price.toFixed(2)}
            </span>
            {product.compare_at_price && (
              <span className="text-xl text-gray-500 line-through">
                ${product.compare_at_price.toFixed(2)}
              </span>
            )}
            {discount && discount > 5 && (
              <span className="badge bg-red-600 text-white">Save {discount}%</span>
            )}
          </div>

          {/* Short description */}
          {product.short_description && (
            <p className="text-gray-300 text-lg leading-relaxed border-t border-dark-700 pt-4">
              {product.short_description}
            </p>
          )}

          {/* Add to cart */}
          <AddToCartSection product={product} />

          {/* Trust badges */}
          <div className="grid grid-cols-3 gap-3 border-t border-dark-700 pt-6">
            {[
              { icon: Truck, title: "Free Shipping", desc: "5-10 business days" },
              { icon: Shield, title: "Secure Pay", desc: "256-bit encryption" },
              { icon: RotateCcw, title: "30-Day Returns", desc: "Hassle-free" },
            ].map(({ icon: Icon, title, desc }) => (
              <div key={title} className="flex flex-col items-center text-center gap-1 p-3 bg-dark-700/50 rounded-xl">
                <Icon className="w-5 h-5 text-brand-400" />
                <p className="text-xs font-semibold text-white">{title}</p>
                <p className="text-xs text-gray-500">{desc}</p>
              </div>
            ))}
          </div>

          {/* Shipping origin */}
          {product.ships_from && (
            <p className="text-sm text-gray-500 flex items-center gap-2">
              <span className="w-2 h-2 bg-green-400 rounded-full" />
              Ships from {product.ships_from} · {product.estimated_delivery_days}
            </p>
          )}
        </div>
      </div>

      {/* Full Description */}
      {product.description && (
        <div className="mt-16 border-t border-dark-700 pt-12">
          <h2 className="text-2xl font-bold text-white mb-6">Product Details</h2>
          <div
            className="prose-store max-w-3xl"
            dangerouslySetInnerHTML={{ __html: product.description }}
          />
        </div>
      )}

      {/* Tags */}
      {product.tags?.length > 0 && (
        <div className="mt-8 flex flex-wrap gap-2">
          {product.tags.map((tag: string) => (
            <span key={tag} className="badge bg-dark-700 text-gray-400 border border-dark-600">
              #{tag}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
