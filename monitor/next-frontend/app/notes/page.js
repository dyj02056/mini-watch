import NotesClient from "../../components/NotesClient";

export default function NotesPage() {
  return (
    <section>
      <h1>관찰 메모</h1>
      <p>서비스를 살펴보며 발견한 내용을 기록합니다.</p>
      <NotesClient />
    </section>
  );
}