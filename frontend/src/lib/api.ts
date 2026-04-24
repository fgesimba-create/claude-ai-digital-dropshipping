const API_BASE = process.env.NEXT_PUBLIC_API_URL
  ? `${process.env.NEXT_PUBLIC_API_URL}/api`
  : "/api";

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...options?.headers },
    next: { revalidate: 0 },
    ...options,
  });
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(error.detail || `API error ${res.status}`);
  }
  return res.json();
}

// Products
export const getProducts = (params?: Record<string, string | number>) => {
  const qs = params ? "?" + new URLSearchParams(params as Record<string, string>).toString() : "";
  return apiFetch<{ products: Product[]; total: number; page: number; pages: number }>(
    `/products${qs}`
  );
};
export const getFeaturedProducts = () => apiFetch<Product[]>("/products/featured");
export const getTrendingProducts = () => apiFetch<Product[]>("/products/trending");
export const getProduct = (slug: string) => apiFetch<Product>(`/products/${slug}`);
export const getCategories = () => apiFetch<Category[]>("/products/categories");

// Checkout
export const createPaymentIntent = (data: CheckoutData) =>
  apiFetch<PaymentIntentResponse>("/orders/create-payment-intent", {
    method: "POST",
    body: JSON.stringify(data),
  });

export const confirmOrder = (data: ConfirmOrderData) =>
  apiFetch<OrderConfirmation>("/orders/confirm", {
    method: "POST",
    body: JSON.stringify(data),
  });

export const getOrderTracking = (orderNumber: string, email: string) =>
  apiFetch<TrackingInfo>(`/orders/${orderNumber}/tracking?email=${encodeURIComponent(email)}`);

// Types
export interface ProductImage {
  url: string;
  alt_text: string;
  is_primary: boolean;
}

export interface Product {
  id: string;
  name: string;
  slug: string;
  short_description?: string;
  description?: string;
  sale_price: number;
  compare_at_price?: number;
  is_featured: boolean;
  is_trending: boolean;
  rating: number;
  review_count: number;
  sale_count: number;
  ships_from?: string;
  estimated_delivery_days?: string;
  category?: { id: string; name: string; slug: string };
  images: ProductImage[];
  tags: string[];
}

export interface Category {
  id: string;
  name: string;
  slug: string;
  icon?: string;
}

export interface CartItem {
  product: Product;
  quantity: number;
}

export interface ShippingAddress {
  line1: string;
  line2?: string;
  city: string;
  state: string;
  zip: string;
  country: string;
  country_code: string;
}

export interface CheckoutData {
  email: string;
  name: string;
  phone?: string;
  shipping_address: ShippingAddress;
  items: { product_id: string; quantity: number }[];
}

export interface PaymentIntentResponse {
  client_secret: string;
  payment_intent_id: string;
  subtotal: number;
  shipping_cost: number;
  tax: number;
  total: number;
}

export interface ConfirmOrderData {
  payment_intent_id: string;
  checkout_data: CheckoutData;
}

export interface OrderConfirmation {
  order_id: string;
  order_number: string;
  status: string;
  message: string;
}

export interface TrackingInfo {
  order_number: string;
  status: string;
  tracking_number?: string;
  tracking_url?: string;
  carrier?: string;
}
