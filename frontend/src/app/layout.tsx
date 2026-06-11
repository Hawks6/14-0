import type { Metadata, Viewport } from "next";
import { Inter, Outfit } from "next/font/google";
import { QueryProvider } from "@/providers/QueryProvider";
import "./globals.css";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
  display: "swap",
});

const outfit = Outfit({
  variable: "--font-outfit",
  subsets: ["latin"],
  display: "swap",
  weight: ["400", "500", "600", "700", "800", "900"],
});

export const metadata: Metadata = {
  title: "14-0 | IPL Draft & Simulation Platform",
  description:
    "Spin for a random historical IPL franchise, draft your dream XI under salary cap constraints, and simulate a 14-match league aiming for the perfect 14-0 season.",
  keywords: [
    "IPL",
    "cricket",
    "draft",
    "simulation",
    "fantasy",
    "14-0",
    "dream team",
  ],
  openGraph: {
    title: "14-0 | IPL Draft & Simulation Platform",
    description:
      "Draft legendary IPL squads. Simulate your way to an unbeaten season.",
    type: "website",
  },
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  themeColor: "#06070d",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${inter.variable} ${outfit.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col bg-background text-foreground">
        <QueryProvider>{children}</QueryProvider>
      </body>
    </html>
  );
}
