export default function DeleteConfirm(props) {
  return (
    <section className="panel">
      <h2>게시글 삭제</h2>
      <p>“{props.post.title}” 게시글을 삭제합니다. 삭제한 게시글는 되돌릴 수 없습니다.</p>
      <div className="actions">
        <button className="danger" onClick={props.onConfirm} disabled={props.busy}>삭제 확인</button>
        <button onClick={props.onCancel} disabled={props.busy}>취소</button>
      </div>
    </section>
  );
}
