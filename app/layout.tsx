import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Kilter Up - AI Training for Climbing",
  description: "AI-powered circuit generation and training planning for Kilterboard",
  icons: {
    icon: '/favicon.svg',
    apple: '/favicon.svg',
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
