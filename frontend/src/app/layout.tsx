import type { Metadata, Viewport } from "next";
import { VT323, Teko } from "next/font/google";
import { QueryProvider } from "@/providers/QueryProvider";
import "./globals.css";

const vt323 = VT323({
  variable: "--font-vt323",
  subsets: ["latin"],
  display: "swap",
  weight: "400",
});

const teko = Teko({
  variable: "--font-teko",
  subsets: ["latin"],
  display: "swap",
  weight: ["300", "400", "500", "600", "700"],
});

export const metadata: Metadata = {
  title: "14-0 | IPL Draft Simulator",
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
    title: "14-0 | IPL Draft Simulator",
    description:
      "Draft legendary IPL squads. Simulate your way to an unbeaten season.",
    type: "website",
  },
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  themeColor: "#1a1a1a",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${vt323.variable} ${teko.variable} h-full antialiased`}
      data-scroll-behavior="smooth"
    >
      <body className="min-h-full flex flex-col bg-[#1a1a1a] text-white">
        <QueryProvider>{children}</QueryProvider>
      </body>
    </html>
  );
}
