"use client";
import Image from "next/image";
import Link from "next/link";
import { Minus, Plus, Trash2, ShoppingCart, ArrowRight, Zap } from "lucide-react";
import { useCartStore } from "@/lib/store";

export default function CartPage() {
  const { items, removeItem, updateQuantity, totalPrice, clearCart } = useCartStore();

  if (items.length === 0) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-32 text-center">
        <div className="w-20 h-20 bg-dark-700 rounded-full flex items-center justify-center mx-auto mb-6">
          <ShoppingCart className="w-10 h-10 text-gray-600" />
        </div>
        <h1 className="text-3xl font-bold text-white mb-3">Your cart is empty</h1>
        <p className="text-gray-500 mb-8">Discover trending tech gadgets to fill it up.</p>
        <Link href="/products" className="btn-primary inline-flex items-center gap-2">
          Shop Products <ArrowRight className="w-4 h-4" />
        </Link>
      </div>
    );
  }

  const subtotal = totalPrice();
  const shipping = 0;
  const total = subtotal + shipping;

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <h1 className="text-3xl font-bold text-white mb-8">Shopping Cart ({items.length})</h1>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Items */}
        <div className="lg:col-span-2 space-y-4">
          {items.map(({ product, quantity }) => {
            const primaryImg = product.images.find((i) => i.is_primary) || product.images[0];
            return (
              <div key={product.id} className="card p-5 flex gap-5">
                {/* Image */}
                <div className="relative w-24 h-24 bg-dark-700 rounded-xl overflow-hidden flex-shrink-0">
                  {primaryImg ? (
                    <Image src={primaryImg.url} alt={product.name} fill className="object-cover" sizes="96px" />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center">
                      <Zap className="w-8 h-8 text-dark-600" />
                    </div>
                  )}
                </div>

                {/* Details */}
                <div className="flex-1 min-w-0">
                  <Link href={`/products/${product.slug}`} className="font-semibold text-white hover:text-brand-300 transition-colors line-clamp-2">
                    {product.name}
                  </Link>
                  {product.category && (
                    <p className="text-xs text-brand-400 mt-1">{product.category.name}</p>
                  )}

                  <div className="flex items-center justify-between mt-4">
                    {/* Qty controls */}
                    <div className="flex items-center bg-dark-700 rounded-lg border border-dark-600">
                      <button onClick={() => updateQuantity(product.id, quantity - 1)} className="p-2 hover:bg-dark-600 rounded-l-lg transition-colors">
                        <Minus className="w-3.5 h-3.5 text-gray-400" />
                      </button>
                      <span className="px-4 text-sm font-semibold text-white">{quantity}</span>
                      <button onClick={() => updateQuantity(product.id, quantity + 1)} className="p-2 hover:bg-dark-600 rounded-r-lg transition-colors">
                        <Plus className="w-3.5 h-3.5 text-gray-400" />
                      </button>
                    </div>

                    <div className="flex items-center gap-4">
                      <span className="font-bold text-white">${(product.sale_price * quantity).toFixed(2)}</span>
                      <button onClick={() => removeItem(product.id)} className="p-2 text-gray-600 hover:text-red-400 transition-colors">
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            );
          })}

          <button onClick={clearCart} className="text-sm text-gray-600 hover:text-red-400 transition-colors mt-2">
            Clear cart
          </button>
        </div>

        {/* Order summary */}
        <div className="lg:col-span-1">
          <div className="card p-6 sticky top-24">
            <h2 className="text-lg font-bold text-white mb-6">Order Summary</h2>
            <div className="space-y-3 text-sm">
              <div className="flex justify-between text-gray-400">
                <span>Subtotal ({items.reduce((s, i) => s + i.quantity, 0)} items)</span>
                <span className="text-white">${subtotal.toFixed(2)}</span>
              </div>
              <div className="flex justify-between text-gray-400">
                <span>Shipping</span>
                <span className="text-green-400 font-medium">Free</span>
              </div>
              <div className="border-t border-dark-700 pt-3 flex justify-between font-bold text-white text-base">
                <span>Total</span>
                <span>${total.toFixed(2)}</span>
              </div>
            </div>

            <Link href="/checkout" className="btn-primary w-full mt-6 flex items-center justify-center gap-2">
              Checkout <ArrowRight className="w-4 h-4" />
            </Link>

            <p className="text-xs text-gray-600 text-center mt-4">
              Secure checkout with Stripe. 256-bit SSL.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
