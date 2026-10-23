import type { Metadata } from "next";
import "./globals.css";
export const metadata: Metadata = { title: "Northstar — Work, in good company", description: "A thoughtful workspace for teams to plan, build and ship together." };
export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) { return <html lang="en"><body>{children}</body></html>; }
