import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'eRTMAC-NWIS — AI-Powered Offset Well Intelligence',
  description: 'Real-Time Drilling Operation Risk & Offset-Well Knowledge Platform',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-[#090D16] text-slate-100 min-h-screen antialiased flex flex-col font-sans selection:bg-cyan-500/30 selection:text-cyan-200">
        {children}
      </body>
    </html>
  );
}
