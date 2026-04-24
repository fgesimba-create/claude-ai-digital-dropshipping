import Link from "next/link";
import { ArrowRight, Zap, TrendingUp, Shield } from "lucide-react";

export function HeroSection() {
  return (
    <section className="relative overflow-hidden bg-dark-900">
      {/* Gradient orbs */}
      <div className="absolute top-0 left-1/4 w-96 h-96 bg-brand-600/20 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-purple-600/10 rounded-full blur-3xl pointer-events-none" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24 md:py-32 relative z-10">
        <div className="text-center max-w-4xl mx-auto">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 bg-brand-900/60 border border-brand-800/60 rounded-full px-4 py-2 mb-8">
            <TrendingUp className="w-4 h-4 text-brand-400" />
            <span className="text-brand-300 text-sm font-medium">AI-Curated Tech Picks Updated Daily</span>
          </div>

          {/* Headline */}
          <h1 className="text-5xl md:text-7xl font-extrabold text-white leading-tight mb-6">
            The Hottest Tech
            <span className="block bg-gradient-to-r from-brand-400 to-purple-400 bg-clip-text text-transparent">
              At Your Fingertips
            </span>
          </h1>

          <p className="text-xl text-gray-400 max-w-2xl mx-auto mb-10 leading-relaxed">
            Trending gadgets and accessories discovered by AI, sourced from top global suppliers,
            delivered fast. No searching required — we find the best so you don&apos;t have to.
          </p>

          {/* CTAs */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-16">
            <Link href="/products" className="btn-primary text-base inline-flex items-center justify-center gap-2">
              Shop Trending Products
              <ArrowRight className="w-5 h-5" />
            </Link>
            <Link href="/products?sort=featured" className="btn-outline text-base inline-flex items-center justify-center gap-2">
              <Zap className="w-5 h-5 text-brand-400" />
              View Featured
            </Link>
          </div>

          {/* Trust indicators */}
          <div className="flex flex-wrap items-center justify-center gap-8 text-sm text-gray-500">
            <div className="flex items-center gap-2">
              <Shield className="w-4 h-4 text-green-400" />
              <span>Secure Checkout</span>
            </div>
            <div className="flex items-center gap-2">
              <Zap className="w-4 h-4 text-brand-400" />
              <span>Ships in 5-10 days</span>
            </div>
            <div className="flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-orange-400" />
              <span>AI-updated daily</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
