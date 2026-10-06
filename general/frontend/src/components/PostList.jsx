export default function PostList(props) {
  return (
    <section className="panel">
      <h2>게시글</h2>
      {props.posts.length === 0 && <p className="muted">아직 게시글가 없습니다.</p>}
      <ul className="post-list">
        {props.posts.map(function (post) {
          return (
            <li key={post.id}>
              <span className="number">{post.id}</span>
              <button className="link" onClick={function () { props.onSelect(post.id); }}>{post.title}</button>
            </li>
          );
        })}
      </ul>
    </section>
  );
}
