import type { Metadata } from "next";
import { Nunito, DM_Sans } from "next/font/google";
import { Analytics } from "@vercel/analytics/react";
import SessionProvider from "@/components/SessionProvider";
import "./globals.css";

const nunito = Nunito({
  variable: "--font-nunito",
  subsets: ["latin"],
  weight: ["400", "500", "600", "700", "800", "900"],
  display: "swap",
});

const dmSans = DM_Sans({
  variable: "--font-dm-sans",
  subsets: ["latin"],
  weight: ["400", "500", "700"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "KashRock API - One API. All Odds. Zero Hassle.",
  description: "The unified sports odds API built for AI-native developers. One endpoint delivers every sportsbook line and DFS slate across all sports. No keys to juggle, no fragmented pricing, no complex schema.",
  keywords: ["sports odds API", "betting API", "DFS API", "sportsbook data", "AI sports data", "unified odds API"],
  openGraph: {
    title: "KashRock API - One API. All Odds. Zero Hassle.",
    description: "Go from idea to odds in minutes. One endpoint, all sports, AI-ready data.",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="scroll-smooth">
      <body
        className={`${nunito.variable} ${dmSans.variable} font-sans antialiased bg-[#F4F1FA] text-[#332F3A]`}
        style={{ fontFamily: "'DM Sans', sans-serif" }}
      >
        <SessionProvider>
          {children}
        </SessionProvider>
        <Analytics />
      </body>
    </html>
  );
}
