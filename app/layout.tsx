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
  title: "Enterprise Esports Data Analytics API | KashRock",
  description:
    "KashRock is an enterprise esports data analytics API — normalized event schedules, market props, player game logs, outcome verification, and media with stable IDs.",
  alternates: {
    canonical: "https://www.kashrock.com/",
  },
  openGraph: {
    title: "Enterprise Esports Data Analytics API | KashRock",
    description:
      "Normalized esports analytics data: event schedules, market props, player logs, outcome verification, and media with stable IDs.",
    url: "https://www.kashrock.com/",
    siteName: "KashRock",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "Enterprise Esports Data Analytics API | KashRock",
    description:
      "Normalized esports analytics: event schedules, market props, player logs, outcome verification, and media.",
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
