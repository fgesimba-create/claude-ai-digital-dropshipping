export const dynamic = "force-dynamic";
import { Suspense } from "react";
import { getFeaturedProducts, getTrendingProducts, getCategories } from "@/lib/api";
import { ProductCard, ProductCardSkeleton } from "@/components/ProductCard";
import { HeroSection } from "@/components/HeroSection";
import Link from "next/link";
import { ArrowRight, Headphones, Home, Gamepad2, Watch, Laptop, Zap, Camera, Lightbulb, Smartphone } from "lucide-react";

const CATEGORY_ICONS: Record<string, React.ElementType> = {
  "wireless-audio": Headphones,
  "smart-home": Home,
  "gaming": Gamepad2,
  "wearables": Watch,
  "laptop-desk": Laptop,
  "led-lighting": Lightbulb,
  "cameras-drones": Camera,
  "mobile-accessories": Smartphone,
};

async function FeaturedProducts() {
  const products = await getFeaturedProducts();
  if (!products?.length) return null;
  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 md:gap-6">
      {products.slice(0, 8).map((product) => (
        <ProductCard key={product.id} product={product} />
      ))}
    </div>
  );
}

async function TrendingProducts() {
  const products = await getTrendingProducts();
  if (!products?.length) return null;
  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 md:gap-6">
      {products.slice(0, 4).map((product) => (
        <ProductCard key={product.id} product={product} />
      ))}
    </div>
  );
}

async function CategoryGrid() {
  const categories = await getCategories();
  if (!categories?.length) return null;
  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
      {categories.slice(0, 8).map((cat) => {
        const Icon = CATEGORY_ICONS[cat.slug] || Zap;
        return (
          <Link
            key={cat.id}
            href={`/products?category=${cat.slug}`}
            className="flex flex-col items-center gap-3 p-5 card hover:border-brand-700/60 hover:bg-dark-700/50 transition-all duration-200 group"
          >
            <div className="w-12 h-12 bg-brand-900/50 rounded-xl flex items-center justify-center group-hover:bg-brand-800/60 transition-colors">
              <Icon className="w-6 h-6 text-brand-400" />
            </div>
            <span className="text-sm font-medium text-gray-300 group-hover:text-white transition-colors text-center">
              {cat.name}
            </span>
          </Link>
        );
      })}
    </div>
  );
}

export default async function HomePage() {
  return (
    <div>
      <HeroSection />

      {/* Categories */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="flex items-center justify-between mb-8">
          <h2 className="text-2xl font-bold text-white">Shop by Category</h2>
          <Link href="/products" className="text-brand-400 hover:text-brand-300 text-sm font-medium flex items-center gap-1">
            View all <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
        <Suspense fallback={
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
            {Array.from({ length: 8 }).map((_, i) => (
              <div key={i} className="card p-5 flex flex-col items-center gap-3">
                <div className="skeleton w-12 h-12 rounded-xl" />
                <div className="skeleton h-4 w-20 rounded" />
              </div>
            ))}
          </div>
        }>
          <CategoryGrid />
        </Suspense>
      </section>

      {/* Featured Products */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h2 className="text-2xl font-bold text-white">Featured Products</h2>
            <p className="text-gray-500 text-sm mt-1">AI-selected top picks just for you</p>
          </div>
          <Link href="/products?sort=featured" className="text-brand-400 hover:text-brand-300 text-sm font-medium flex items-center gap-1">
            See all <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
        <Suspense fallback={
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 md:gap-6">
            {Array.from({ length: 8 }).map((_, i) => <ProductCardSkeleton key={i} />)}
          </div>
        }>
          <FeaturedProducts />
        </Suspense>
      </section>

      {/* Trending */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h2 className="text-2xl font-bold text-white">🔥 Trending Now</h2>
            <p className="text-gray-500 text-sm mt-1">What everyone&apos;s buying this week</p>
          </div>
          <Link href="/products?sort=trending" className="text-brand-400 hover:text-brand-300 text-sm font-medium flex items-center gap-1">
            See all <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
        <Suspense fallback={
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 md:gap-6">
            {Array.from({ length: 4 }).map((_, i) => <ProductCardSkeleton key={i} />)}
          </div>
        }>
          <TrendingProducts />
        </Suspense>
      </section>

      {/* Value proposition banner */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="bg-gradient-to-r from-brand-900/50 to-dark-800 border border-brand-800/50 rounded-2xl p-8 md:p-12 text-center">
          <h2 className="text-3xl font-bold text-white mb-4">
            Tech You Need, Prices You&apos;ll Love
          </h2>
          <p className="text-gray-400 max-w-2xl mx-auto mb-8 leading-relaxed">
            Our AI scans thousands of products daily to find the best trending tech accessories
            at the best prices — so you always get the hottest gear without paying retail.
          </p>
          <Link href="/products" className="btn-primary inline-flex items-center gap-2">
            Shop Now <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </section>
    </div>
  );
}
