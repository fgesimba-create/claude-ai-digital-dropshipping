export const dynamic = "force-dynamic";
import { Suspense } from "react";
import { getProducts, getCategories } from "@/lib/api";
import { ProductCard, ProductCardSkeleton } from "@/components/ProductCard";
import { ProductFilters } from "@/components/ProductFilters";
import { SlidersHorizontal } from "lucide-react";

interface PageProps {
  searchParams: Promise<{
    category?: string;
    sort?: string;
    search?: string;
    page?: string;
    min_price?: string;
    max_price?: string;
  }>;
}

async function ProductGrid({ searchParams }: { searchParams: Awaited<PageProps["searchParams"]> }) {
  const params: Record<string, string | number> = { page: 1, limit: 24 };
  if (searchParams.category) params.category = searchParams.category;
  if (searchParams.sort) params.sort = searchParams.sort;
  if (searchParams.search) params.search = searchParams.search;
  if (searchParams.page) params.page = parseInt(searchParams.page);
  if (searchParams.min_price) params.min_price = searchParams.min_price;
  if (searchParams.max_price) params.max_price = searchParams.max_price;

  const data = await getProducts(params);

  if (!data.products?.length) {
    return (
      <div className="col-span-full flex flex-col items-center justify-center py-24 text-center">
        <div className="w-16 h-16 bg-dark-700 rounded-full flex items-center justify-center mb-4">
          <SlidersHorizontal className="w-8 h-8 text-gray-600" />
        </div>
        <h3 className="text-xl font-semibold text-white mb-2">No products found</h3>
        <p className="text-gray-500">Our AI is discovering products. Check back soon!</p>
      </div>
    );
  }

  return (
    <>
      <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-4 gap-4 md:gap-6">
        {data.products.map((product) => (
          <ProductCard key={product.id} product={product} />
        ))}
      </div>
      {data.pages > 1 && (
        <div className="flex justify-center gap-2 mt-10">
          {Array.from({ length: data.pages }).map((_, i) => (
            <a
              key={i}
              href={`?page=${i + 1}${searchParams.category ? `&category=${searchParams.category}` : ""}${searchParams.sort ? `&sort=${searchParams.sort}` : ""}`}
              className={`w-10 h-10 rounded-lg flex items-center justify-center text-sm font-medium transition-colors ${
                (searchParams.page ? parseInt(searchParams.page) : 1) === i + 1
                  ? "bg-brand-600 text-white"
                  : "bg-dark-700 text-gray-400 hover:bg-dark-600 hover:text-white"
              }`}
            >
              {i + 1}
            </a>
          ))}
        </div>
      )}
    </>
  );
}

export default async function ProductsPage({ searchParams }: PageProps) {
  const params = await searchParams;
  const categories = await getCategories();

  const sortOptions = [
    { value: "featured", label: "Featured" },
    { value: "trending", label: "Trending" },
    { value: "newest", label: "Newest" },
    { value: "price_asc", label: "Price: Low to High" },
    { value: "price_desc", label: "Price: High to Low" },
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <div className="flex flex-col md:flex-row gap-8">
        {/* Sidebar Filters */}
        <aside className="w-full md:w-56 flex-shrink-0">
          <ProductFilters categories={categories} sortOptions={sortOptions} searchParams={params} />
        </aside>

        {/* Main Grid */}
        <div className="flex-1">
          <div className="flex items-center justify-between mb-6">
            <h1 className="text-2xl font-bold text-white">
              {params.category
                ? categories.find((c) => c.slug === params.category)?.name || "Products"
                : params.sort === "trending"
                ? "Trending Products"
                : "All Products"}
            </h1>
          </div>

          <Suspense
            key={JSON.stringify(params)}
            fallback={
              <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-4 gap-4 md:gap-6">
                {Array.from({ length: 12 }).map((_, i) => <ProductCardSkeleton key={i} />)}
              </div>
            }
          >
            <ProductGrid searchParams={params} />
          </Suspense>
        </div>
      </div>
    </div>
  );
}
