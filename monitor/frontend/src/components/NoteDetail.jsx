export default function NoteDetail(props) {
  if (props.note === null) {
    return (
      <section className="panel">
        <h2>메모 상세</h2>
        <p className="muted">목록에서 제목을 선택해 주세요.</p>
      </section>
    );
  }
  return (
    <section className="panel">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <p className="muted">메모 #{props.note.id}</p>
        <span
          className="badge"
          style={{
            padding: "4px 8px",
            borderRadius: "4px",
            backgroundColor: "#e2e8f0",
            fontSize: "0.85rem",
            fontWeight: "600",
          }}
        >
          {props.note.status || "확인 전"}
        </span>
      </div>
      <h2>{props.note.title}</h2>
      <p className="body-text">{props.note.body}</p>
      <div className="actions">
        <button onClick={props.onEdit}>수정</button>
        <button className="danger" onClick={props.onDelete}>삭제</button>
      </div>
    </section>
  );
}