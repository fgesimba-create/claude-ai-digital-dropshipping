import Link from "next/link";
import { ArrowLeft } from "lucide-react";

export default function NotFound() {
  return (
    <div className="max-w-2xl mx-auto px-4 py-32 text-center">
      <p className="text-8xl font-black text-dark-700 mb-6">404</p>
      <h1 className="text-3xl font-bold text-white mb-3">Page Not Found</h1>
      <p className="text-gray-500 mb-8">The page you&apos;re looking for doesn&apos;t exist.</p>
      <Link href="/" className="btn-primary inline-flex items-center gap-2">
        <ArrowLeft className="w-4 h-4" />
        Back to Home
      </Link>
    </div>
  );
}
