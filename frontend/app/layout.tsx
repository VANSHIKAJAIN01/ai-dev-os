import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI Dev OS",
  description: "AI Operating System for Developers",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="h-full">
      <body className="bg-gray-950 text-gray-100 min-h-screen antialiased h-full">
        {children}
      </body>
    </html>
  );
}
