"use client";
import { useState, useEffect } from "react";
import { useCartStore } from "@/lib/store";
import { createPaymentIntent, confirmOrder } from "@/lib/api";
import { loadStripe } from "@stripe/stripe-js";
import { Elements, PaymentElement, useStripe, useElements } from "@stripe/react-stripe-js";
import { Shield, Lock, ArrowLeft } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";

const stripePromise = loadStripe(process.env.NEXT_PUBLIC_STRIPE_KEY || "");

function CheckoutForm({
  clientSecret,
  paymentIntentId,
  formData,
  onSuccess,
}: {
  clientSecret: string;
  paymentIntentId: string;
  formData: Record<string, string>;
  onSuccess: (orderNumber: string) => void;
}) {
  const stripe = useStripe();
  const elements = useElements();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const { items, clearCart } = useCartStore();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!stripe || !elements) return;
    setLoading(true);
    setError("");

    const { error: stripeError } = await stripe.confirmPayment({
      elements,
      redirect: "if_required",
    });

    if (stripeError) {
      setError(stripeError.message || "Payment failed");
      setLoading(false);
      return;
    }

    try {
      const result = await confirmOrder({
        payment_intent_id: paymentIntentId,
        checkout_data: {
          email: formData.email,
          name: `${formData.firstName} ${formData.lastName}`,
          phone: formData.phone,
          shipping_address: {
            line1: formData.address,
            line2: formData.address2,
            city: formData.city,
            state: formData.state,
            zip: formData.zip,
            country: "United States",
            country_code: "US",
          },
          items: items.map((i) => ({ product_id: i.product.id, quantity: i.quantity })),
        },
      });

      clearCart();
      onSuccess(result.order_number);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Order confirmation failed. Contact support.");
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <PaymentElement options={{ layout: "tabs" }} />
      {error && (
        <div className="p-4 bg-red-900/30 border border-red-800 rounded-lg text-red-300 text-sm">
          {error}
        </div>
      )}
      <button
        type="submit"
        disabled={loading || !stripe}
        className="btn-primary w-full py-4 text-base flex items-center justify-center gap-2"
      >
        <Lock className="w-4 h-4" />
        {loading ? "Processing..." : `Pay $${useCartStore.getState().totalPrice().toFixed(2)}`}
      </button>
    </form>
  );
}

export default function CheckoutPage() {
  const { items, totalPrice } = useCartStore();
  const router = useRouter();
  const [step, setStep] = useState<"info" | "payment" | "success">("info");
  const [clientSecret, setClientSecret] = useState("");
  const [paymentIntentId, setPaymentIntentId] = useState("");
  const [orderNumber, setOrderNumber] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [formData, setFormData] = useState({
    email: "", firstName: "", lastName: "", phone: "",
    address: "", address2: "", city: "", state: "", zip: "",
  });

  useEffect(() => {
    if (items.length === 0 && step !== "success") {
      router.push("/cart");
    }
  }, [items, step, router]);

  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    setFormData((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  }

  async function handleInfoSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const result = await createPaymentIntent({
        email: formData.email,
        name: `${formData.firstName} ${formData.lastName}`,
        phone: formData.phone,
        shipping_address: {
          line1: formData.address,
          line2: formData.address2,
          city: formData.city,
          state: formData.state,
          zip: formData.zip,
          country: "United States",
          country_code: "US",
        },
        items: items.map((i) => ({ product_id: i.product.id, quantity: i.quantity })),
      });
      setClientSecret(result.client_secret);
      setPaymentIntentId(result.payment_intent_id);
      setStep("payment");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to start checkout");
    } finally {
      setLoading(false);
    }
  }

  if (step === "success") {
    return (
      <div className="max-w-2xl mx-auto px-4 py-24 text-center">
        <div className="w-20 h-20 bg-green-900/40 border border-green-800 rounded-full flex items-center justify-center mx-auto mb-6">
          <Shield className="w-10 h-10 text-green-400" />
        </div>
        <h1 className="text-3xl font-bold text-white mb-3">Order Confirmed!</h1>
        <p className="text-gray-400 mb-4">Order #{orderNumber}</p>
        <p className="text-gray-500 mb-8 leading-relaxed">
          Thanks for your purchase! You&apos;ll receive a confirmation email shortly,
          followed by tracking information once your order ships (typically 5-10 business days).
        </p>
        <Link href="/products" className="btn-primary inline-flex items-center gap-2">
          Continue Shopping
        </Link>
      </div>
    );
  }

  const total = totalPrice();

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <Link href="/cart" className="flex items-center gap-2 text-gray-500 hover:text-white transition-colors mb-8 text-sm">
        <ArrowLeft className="w-4 h-4" /> Back to cart
      </Link>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
        {/* Form */}
        <div>
          <h1 className="text-2xl font-bold text-white mb-8">
            {step === "info" ? "Shipping Information" : "Payment"}
          </h1>

          {step === "info" ? (
            <form onSubmit={handleInfoSubmit} className="space-y-4">
              <input required name="email" type="email" placeholder="Email address" value={formData.email} onChange={handleChange} className="input" />
              <div className="grid grid-cols-2 gap-4">
                <input required name="firstName" placeholder="First name" value={formData.firstName} onChange={handleChange} className="input" />
                <input required name="lastName" placeholder="Last name" value={formData.lastName} onChange={handleChange} className="input" />
              </div>
              <input name="phone" type="tel" placeholder="Phone (optional)" value={formData.phone} onChange={handleChange} className="input" />
              <input required name="address" placeholder="Street address" value={formData.address} onChange={handleChange} className="input" />
              <input name="address2" placeholder="Apt, suite, etc. (optional)" value={formData.address2} onChange={handleChange} className="input" />
              <div className="grid grid-cols-3 gap-4">
                <input required name="city" placeholder="City" value={formData.city} onChange={handleChange} className="input col-span-1" />
                <input required name="state" placeholder="State" value={formData.state} onChange={handleChange} className="input" />
                <input required name="zip" placeholder="ZIP" value={formData.zip} onChange={handleChange} className="input" />
              </div>
              {error && <p className="text-red-400 text-sm">{error}</p>}
              <button type="submit" disabled={loading} className="btn-primary w-full py-4 text-base mt-2">
                {loading ? "Loading..." : "Continue to Payment"}
              </button>
            </form>
          ) : (
            clientSecret && (
              <Elements stripe={stripePromise} options={{ clientSecret }}>
                <CheckoutForm
                  clientSecret={clientSecret}
                  paymentIntentId={paymentIntentId}
                  formData={formData}
                  onSuccess={(num) => { setOrderNumber(num); setStep("success"); }}
                />
              </Elements>
            )
          )}
        </div>

        {/* Order summary */}
        <div>
          <div className="card p-6 sticky top-24">
            <h2 className="font-bold text-white mb-4">Order Summary</h2>
            <div className="space-y-4 mb-6">
              {items.map(({ product, quantity }) => (
                <div key={product.id} className="flex justify-between text-sm">
                  <span className="text-gray-300 line-clamp-1 flex-1 mr-4">
                    {product.name} × {quantity}
                  </span>
                  <span className="text-white font-medium flex-shrink-0">
                    ${(product.sale_price * quantity).toFixed(2)}
                  </span>
                </div>
              ))}
            </div>
            <div className="border-t border-dark-700 pt-4 space-y-2 text-sm">
              <div className="flex justify-between text-gray-400">
                <span>Subtotal</span><span>${total.toFixed(2)}</span>
              </div>
              <div className="flex justify-between text-gray-400">
                <span>Shipping</span><span className="text-green-400">Free</span>
              </div>
              <div className="flex justify-between font-bold text-white text-base pt-2 border-t border-dark-700">
                <span>Total</span><span>${total.toFixed(2)}</span>
              </div>
            </div>
            <div className="flex items-center gap-2 mt-6 text-xs text-gray-600 justify-center">
              <Lock className="w-3.5 h-3.5" />
              Secured by Stripe
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
