import type { Metadata } from "next";
import { Nunito, DM_Sans } from "next/font/google";
import { Analytics } from "@vercel/analytics/react";
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
  title: "Esports DFS API | KashRock",
  description: "Normalized esports DFS API with slates, props, player game logs, results grading and media. Build bots, dashboards, and models without scraping.",
  keywords: ["esports DFS API", "esports props", "player game logs", "results grading", "CS2 API", "LoL API", "Dota 2 API"],
  openGraph: {
    title: "Esports DFS API | KashRock",
    description: "Esports-first infrastructure: slates, props, results + grading. Build bots and dashboards without scraping.",
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
        {children}
        <Analytics />
      </body>
    </html>
  );
}
