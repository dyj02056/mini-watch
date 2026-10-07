import { useState } from "react";

export default function NoteForm(props) {
  const [title, setTitle] = useState(props.note?.title || "");
  const [body, setBody] = useState(props.note?.body || "");
  const [status, setStatus] = useState(props.note?.status || "확인 전");

  function handleSubmit(event) {
    event.preventDefault();
    props.onSave(title, body, status);
  }

  return (
    <section className="panel">
      <h2>{props.heading}</h2>
      <form onSubmit={handleSubmit}>
        <label>
          제목
          <input
            value={title}
            onChange={function (event) {
              setTitle(event.target.value);
            }}
          />
        </label>
        <label>
          처리 상태
          <select
            value={status}
            onChange={function (event) {
              setStatus(event.target.value);
            }}
          >
            <option value="확인 전">확인 전</option>
            <option value="확인 중">확인 중</option>
            <option value="완료">완료</option>
          </select>
        </label>
        <label>
          내용
          <textarea
            value={body}
            onChange={function (event) {
              setBody(event.target.value);
            }}
          />
        </label>
        <div className="actions">
          <button className="primary" type="submit" disabled={props.busy}>저장</button>
          <button type="button" onClick={props.onCancel} disabled={props.busy}>취소</button>
        </div>
      </form>
    </section>
  );
}