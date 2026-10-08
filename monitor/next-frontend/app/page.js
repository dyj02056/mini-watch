import Link from "next/link";
import Counter from "../components/Counter";

export default function HomePage() {
  return (
    <section>
      <h1>관찰 메모 시작하기</h1>
      <p>Next.js로 메모 화면을 준비합니다.</p>
      <Link href="/notes">메모 화면으로 이동</Link>
      <Counter />
    </section>
  );
}