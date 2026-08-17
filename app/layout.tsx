import type { Metadata } from "next";
import "./globals.css";
import "../features/workspace/workspace-shell.css";

export const metadata: Metadata = {
  title: "设计智能工作台",
  description: "基于已有 Logo 生成统一、克制、现代的品牌视觉延展与二维平面应用。",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="zh-CN"><body>{children}</body></html>;
}
