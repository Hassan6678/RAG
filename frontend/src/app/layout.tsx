import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "DocMind AI",
  description: "AI Research & Analytics Workspace",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="font-sans antialiased bg-[#F0F4F8] text-gray-900">
        {children}
      </body>
    </html>
  );
}
