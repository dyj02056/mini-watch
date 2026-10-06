export default function PostDetail(props) {
  if (props.post === null) {
    return <section className="panel"><h2>게시글 상세</h2><p className="muted">목록에서 제목을 선택해 주세요.</p></section>;
  }
  return (
    <section className="panel">
      <p className="muted">게시글 {props.post.id}</p>
      <h2>{props.post.title}</h2>
      <p className="body-text">{props.post.body}</p>
      <div className="actions">
        <button onClick={props.onEdit}>수정</button>
        <button className="danger" onClick={props.onDelete}>삭제</button>
      </div>
    </section>
  );
}
