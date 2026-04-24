"use client";
import { useState } from "react";
import Link from "next/link";
import { ShoppingCart, Zap, Menu, X, Search } from "lucide-react";
import { useCartStore } from "@/lib/store";
import { clsx } from "clsx";

export function Navbar() {
  const [isOpen, setIsOpen] = useState(false);
  const totalItems = useCartStore((s) => s.totalItems());

  return (
    <nav className="sticky top-0 z-50 bg-dark-900/95 backdrop-blur-md border-b border-dark-700">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-2 group">
            <div className="w-8 h-8 bg-brand-600 rounded-lg flex items-center justify-center group-hover:bg-brand-500 transition-colors">
              <Zap className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold text-white">TechFlow</span>
          </Link>

          {/* Desktop nav */}
          <div className="hidden md:flex items-center gap-8">
            <Link href="/products" className="text-gray-400 hover:text-white transition-colors text-sm font-medium">
              All Products
            </Link>
            <Link href="/products?sort=trending" className="text-gray-400 hover:text-white transition-colors text-sm font-medium">
              Trending
            </Link>
            <Link href="/products?category=wireless-audio" className="text-gray-400 hover:text-white transition-colors text-sm font-medium">
              Audio
            </Link>
            <Link href="/products?category=gaming" className="text-gray-400 hover:text-white transition-colors text-sm font-medium">
              Gaming
            </Link>
            <Link href="/products?category=smart-home" className="text-gray-400 hover:text-white transition-colors text-sm font-medium">
              Smart Home
            </Link>
          </div>

          {/* Right side */}
          <div className="flex items-center gap-3">
            <Link href="/products" className="hidden md:flex items-center gap-2 text-gray-400 hover:text-white transition-colors">
              <Search className="w-5 h-5" />
            </Link>

            <Link href="/cart" className="relative p-2 hover:bg-dark-700 rounded-lg transition-colors">
              <ShoppingCart className="w-5 h-5 text-gray-300" />
              {totalItems > 0 && (
                <span className="absolute -top-1 -right-1 w-5 h-5 bg-brand-600 rounded-full text-xs font-bold text-white flex items-center justify-center">
                  {totalItems > 9 ? "9+" : totalItems}
                </span>
              )}
            </Link>

            <button
              className="md:hidden p-2 hover:bg-dark-700 rounded-lg transition-colors"
              onClick={() => setIsOpen(!isOpen)}
            >
              {isOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile menu */}
      {isOpen && (
        <div className="md:hidden bg-dark-800 border-t border-dark-700 px-4 py-4 space-y-3">
          {["All Products", "Trending", "Wireless Audio", "Gaming", "Smart Home"].map((item) => (
            <Link
              key={item}
              href={`/products${item !== "All Products" ? `?category=${item.toLowerCase().replace(/ /g, "-")}` : ""}`}
              className="block text-gray-300 hover:text-white py-2 text-sm font-medium"
              onClick={() => setIsOpen(false)}
            >
              {item}
            </Link>
          ))}
        </div>
      )}
    </nav>
  );
}
