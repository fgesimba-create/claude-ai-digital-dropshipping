import Link from "next/link";
import { Zap, Shield, Truck, RotateCcw } from "lucide-react";

export function Footer() {
  return (
    <footer className="bg-dark-800 border-t border-dark-700 mt-20">
      {/* Trust bar */}
      <div className="border-b border-dark-700">
        <div className="max-w-7xl mx-auto px-4 py-8 grid grid-cols-2 md:grid-cols-4 gap-6">
          {[
            { icon: Truck, title: "Free Shipping", desc: "On all orders worldwide" },
            { icon: Shield, title: "Secure Checkout", desc: "256-bit SSL encryption" },
            { icon: RotateCcw, title: "Easy Returns", desc: "30-day hassle-free returns" },
            { icon: Zap, title: "Fast Processing", desc: "Orders ship in 1-2 days" },
          ].map(({ icon: Icon, title, desc }) => (
            <div key={title} className="flex items-start gap-3">
              <div className="w-10 h-10 bg-brand-900/50 rounded-lg flex items-center justify-center flex-shrink-0">
                <Icon className="w-5 h-5 text-brand-400" />
              </div>
              <div>
                <p className="font-semibold text-white text-sm">{title}</p>
                <p className="text-gray-500 text-xs mt-0.5">{desc}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Links */}
      <div className="max-w-7xl mx-auto px-4 py-10 grid grid-cols-2 md:grid-cols-4 gap-8">
        <div>
          <div className="flex items-center gap-2 mb-4">
            <div className="w-7 h-7 bg-brand-600 rounded-lg flex items-center justify-center">
              <Zap className="w-4 h-4 text-white" />
            </div>
            <span className="font-bold text-white">TechFlow</span>
          </div>
          <p className="text-gray-500 text-sm leading-relaxed">
            AI-curated tech accessories. Always trending, always quality.
          </p>
        </div>
        <div>
          <h4 className="font-semibold text-white mb-3 text-sm">Shop</h4>
          <ul className="space-y-2 text-sm text-gray-400">
            {["All Products", "Trending", "Wireless Audio", "Gaming", "Smart Home", "Wearables"].map((item) => (
              <li key={item}><Link href="/products" className="hover:text-white transition-colors">{item}</Link></li>
            ))}
          </ul>
        </div>
        <div>
          <h4 className="font-semibold text-white mb-3 text-sm">Support</h4>
          <ul className="space-y-2 text-sm text-gray-400">
            {["Track Order", "Returns", "FAQ", "Contact Us"].map((item) => (
              <li key={item}><Link href="#" className="hover:text-white transition-colors">{item}</Link></li>
            ))}
          </ul>
        </div>
        <div>
          <h4 className="font-semibold text-white mb-3 text-sm">Legal</h4>
          <ul className="space-y-2 text-sm text-gray-400">
            {["Privacy Policy", "Terms of Service", "Cookie Policy"].map((item) => (
              <li key={item}><Link href="#" className="hover:text-white transition-colors">{item}</Link></li>
            ))}
          </ul>
        </div>
      </div>

      <div className="border-t border-dark-700 py-5 text-center text-gray-600 text-xs">
        © {new Date().getFullYear()} TechFlow. All rights reserved. Powered by AI.
      </div>
    </footer>
  );
}
