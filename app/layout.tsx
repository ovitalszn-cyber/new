import type { Metadata } from "next";
import { Nunito, DM_Sans } from "next/font/google";
import { Analytics } from "@vercel/analytics/react";
import MaintenanceOverlay from "@/components/MaintenanceOverlay";
import { SessionProvider } from "@/components/auth/SessionProvider";
import { MAINTENANCE_MODE } from "@/lib/maintenance";
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

const HOME_TITLE =
  "Esports Data API — CS2, LoL & Dota Props, Odds & Stats | KashRock"
const HOME_DESCRIPTION =
  "Affordable esports data API. Normalized CS2, LoL & Dota player props, lines, and stats from PrizePicks, Underdog & more. Instant API key, free tier — no enterprise pricing."

export const metadata: Metadata = {
  metadataBase: new URL("https://www.kashrock.com"),
  title: {
    default: HOME_TITLE,
    template: "%s | KashRock",
  },
  description: HOME_DESCRIPTION,
  alternates: {
    canonical: "https://www.kashrock.com/",
  },
  openGraph: {
    title: HOME_TITLE,
    description: HOME_DESCRIPTION,
    url: "https://www.kashrock.com/",
    siteName: "KashRock",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: HOME_TITLE,
    description: HOME_DESCRIPTION,
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
        {MAINTENANCE_MODE ? (
          <MaintenanceOverlay />
        ) : (
          <SessionProvider>
            {children}
            <Analytics />
          </SessionProvider>
        )}
      </body>
    </html>
  );
}
