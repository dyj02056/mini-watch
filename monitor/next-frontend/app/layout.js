import Link from "next/link";
import "./globals.css";

export const metadata = {
  title: "Mini Watch 메모",
  description: "Next.js로 만드는 관찰 메모 화면",
};

export default function RootLayout({ children }) {
  return (
    <html lang="ko">
      <body>
        <header>
          <strong>Mini Watch</strong>
          <nav aria-label="주 메뉴">
            <Link href="/">처음</Link>
            <Link href="/notes">관찰 메모</Link>
          </nav>
        </header>
        <main>{children}</main>
      </body>
    </html>
  );
}