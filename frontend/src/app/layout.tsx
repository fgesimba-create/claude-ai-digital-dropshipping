import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Navbar } from "@/components/Navbar";
import { Footer } from "@/components/Footer";
import { Providers } from "@/components/Providers";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });

export const metadata: Metadata = {
  title: {
    default: "TechFlow — Premium Tech Accessories",
    template: "%s | TechFlow",
  },
  description:
    "Discover the hottest trending tech accessories at unbeatable prices. Free shipping on all orders. Smart home, wireless audio, gaming gear, and more.",
  keywords: ["tech accessories", "gadgets", "smart home", "wireless earbuds", "gaming"],
  openGraph: {
    type: "website",
    siteName: "TechFlow",
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={inter.variable}>
      <body className="bg-dark-900 text-white min-h-screen font-sans antialiased">
        <Providers>
          <Navbar />
          <main className="min-h-[calc(100vh-64px)]">{children}</main>
          <Footer />
        </Providers>
      </body>
    </html>
  );
}
