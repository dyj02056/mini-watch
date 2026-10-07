export default function NoteList(props) {
  return (
    <section className="panel">
      <h2>관찰 메모</h2>
      {props.notes.length === 0 && <p className="muted">아직 관찰 메모가 없습니다.</p>}
      <ul className="note-list">
        {props.notes.map(function (note) {
          return (
            <li
              key={note.id}
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                padding: "4px 0",
              }}
            >
              <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                <span className="number">{note.id}</span>
                <button
                  className="link"
                  onClick={function () {
                    props.onSelect(note.id);
                  }}
                >
                  {note.title}
                </button>
              </div>
              <span
                style={{
                  fontSize: "0.8rem",
                  color: "#64748b",
                  marginLeft: "8px",
                  whiteSpace: "nowrap",
                }}
              >
                {note.status || "확인 전"}
              </span>
            </li>
          );
        })}
      </ul>
    </section>
  );
}