import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Salud Mental IA",
  description: "Plataforma inteligente de asistencia emocional basada en IA generativa.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="es" className="h-full antialiased">
      <body className="min-h-full flex flex-col">{children}</body>
    </html>
  );
}
