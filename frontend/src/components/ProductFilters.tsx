"use client";
import { useRouter, useSearchParams } from "next/navigation";
import type { Category } from "@/lib/api";

interface Props {
  categories: Category[];
  sortOptions: { value: string; label: string }[];
  searchParams: Record<string, string | undefined>;
}

export function ProductFilters({ categories, sortOptions, searchParams }: Props) {
  const router = useRouter();

  function updateParam(key: string, value: string | null) {
    const params = new URLSearchParams();
    Object.entries(searchParams).forEach(([k, v]) => {
      if (v && k !== key && k !== "page") params.set(k, v);
    });
    if (value) params.set(key, value);
    router.push(`/products?${params.toString()}`);
  }

  return (
    <div className="space-y-6">
      {/* Search */}
      <div>
        <label className="block text-sm font-semibold text-gray-300 mb-2">Search</label>
        <input
          type="text"
          placeholder="Search products..."
          defaultValue={searchParams.search || ""}
          className="input text-sm"
          onChange={(e) => {
            const val = e.target.value;
            if (val.length > 2 || val.length === 0) updateParam("search", val || null);
          }}
        />
      </div>

      {/* Sort */}
      <div>
        <label className="block text-sm font-semibold text-gray-300 mb-2">Sort By</label>
        <div className="space-y-1">
          {sortOptions.map((opt) => (
            <button
              key={opt.value}
              onClick={() => updateParam("sort", opt.value)}
              className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors ${
                (searchParams.sort || "featured") === opt.value
                  ? "bg-brand-900/60 text-brand-300 border border-brand-800/60"
                  : "text-gray-400 hover:text-white hover:bg-dark-700"
              }`}
            >
              {opt.label}
            </button>
          ))}
        </div>
      </div>

      {/* Categories */}
      <div>
        <label className="block text-sm font-semibold text-gray-300 mb-2">Category</label>
        <div className="space-y-1">
          <button
            onClick={() => updateParam("category", null)}
            className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors ${
              !searchParams.category
                ? "bg-brand-900/60 text-brand-300 border border-brand-800/60"
                : "text-gray-400 hover:text-white hover:bg-dark-700"
            }`}
          >
            All Categories
          </button>
          {categories.map((cat) => (
            <button
              key={cat.id}
              onClick={() => updateParam("category", cat.slug)}
              className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors ${
                searchParams.category === cat.slug
                  ? "bg-brand-900/60 text-brand-300 border border-brand-800/60"
                  : "text-gray-400 hover:text-white hover:bg-dark-700"
              }`}
            >
              {cat.name}
            </button>
          ))}
        </div>
      </div>

      {/* Price Range */}
      <div>
        <label className="block text-sm font-semibold text-gray-300 mb-2">Price Range</label>
        <div className="flex items-center gap-2">
          <input
            type="number"
            placeholder="Min"
            defaultValue={searchParams.min_price || ""}
            className="input text-sm w-full"
            onBlur={(e) => updateParam("min_price", e.target.value || null)}
          />
          <span className="text-gray-600">—</span>
          <input
            type="number"
            placeholder="Max"
            defaultValue={searchParams.max_price || ""}
            className="input text-sm w-full"
            onBlur={(e) => updateParam("max_price", e.target.value || null)}
          />
        </div>
      </div>

      {/* Clear */}
      {(searchParams.category || searchParams.sort || searchParams.search) && (
        <button
          onClick={() => router.push("/products")}
          className="w-full btn-outline text-sm py-2"
        >
          Clear Filters
        </button>
      )}
    </div>
  );
}
