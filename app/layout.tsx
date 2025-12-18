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
  metadataBase: new URL("https://www.kashrock.com"),
  title: "Esports DFS API | KashRock",
  description:
    "KashRock is a DFS esports API for builders — slates, props, player game logs, results grading, and media with stable IDs.",
  alternates: {
    canonical: "https://www.kashrock.com/",
  },
  openGraph: {
    title: "Esports DFS API | KashRock",
    description:
      "Slates, props, player game logs, results grading, and media. Normalized esports DFS data with stable IDs.",
    url: "https://www.kashrock.com/",
    siteName: "KashRock",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "Esports DFS API | KashRock",
    description:
      "Normalized esports DFS data: slates, props, player logs, results grading, and media.",
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
