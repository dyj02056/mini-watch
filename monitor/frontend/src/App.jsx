export default function App() {
  const serviceName = "감시 서비스";

  return (
    <main className="shell">
      <section className="panel">
        <h1>{serviceName}</h1>
        <p>요청 기록을 살펴보고 관찰 메모를 남깁니다.</p>
        <p className="muted">다음 시간에는 운영자 로그인 화면을 만듭니다.</p>
      </section>
    </main>
  );
}