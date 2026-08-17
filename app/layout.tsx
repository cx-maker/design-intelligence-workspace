import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = { title: "设计智能工作台", description: "用于确定视觉方向的轻量工作台。" };
export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) { return <html lang="zh-CN"><body>{children}</body></html>; }
