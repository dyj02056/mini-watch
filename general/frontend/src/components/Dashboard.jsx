import { useEffect, useState } from "react";
import { getPosts, getPost, createPost, updatePost, removePost } from "../api/posts.js";
import PostList from "./PostList.jsx";
import PostDetail from "./PostDetail.jsx";
import PostForm from "./PostForm.jsx";
import DeleteConfirm from "./DeleteConfirm.jsx";

export default function Dashboard(props) {
  const [posts, setPosts] = useState([]);
  const [selected, setSelected] = useState(null);
  const [screen, setScreen] = useState("detail");
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");

  async function loadData() {
    props.onClearError();
    setLoading(true);
    try {
      const postsData = await getPosts();
      setPosts(postsData.posts);
    } catch (error) {
      props.onError(error);
    } finally {
      setLoading(false);
    }
  }

  useEffect(function () {
    loadData();
  }, []);

  async function selectPost(id) {
    props.onClearError();
    if (busy) return;
    setMessage("");
    try {
      const data = await getPost(id);
      setSelected(data.post);
      setScreen("detail");
    } catch (error) {
      setSelected(null);
      setScreen("detail");
      props.onError(error);
    }
  }

  function startNew() {
    props.onClearError();
    setMessage("");
    setScreen("new");
  }

  async function savePost(title, body) {
    props.onClearError();
    setBusy(true);
    setMessage("");
    try {
      let data;
      if (screen === "new") {
        data = await createPost(title, body, props.csrfToken);
      } else {
        data = await updatePost(selected.id, title, body, props.csrfToken);
      }
      setSelected(data.post);
      setScreen("detail");
      setMessage("게시글을 저장했습니다.");
      await loadData();
    } catch (error) {
      props.onError(error);
    } finally {
      setBusy(false);
    }
  }

  async function deletePost() {
    props.onClearError();
    setBusy(true);
    setMessage("");
    try {
      const data = await removePost(selected.id, props.csrfToken);
      setSelected(null);
      setScreen("detail");
      setMessage(data.message);
      await loadData();
    } catch (error) {
      props.onError(error);
    } finally {
      setBusy(false);
    }
  }

  let content;
  if (screen === "new") {
    content = <PostForm key="new" heading="새 게시글" post={{ title: "", body: "" }} onSave={savePost} onCancel={function () { setScreen("detail"); }} busy={busy} />;
  } else if (screen === "edit") {
    content = <PostForm key="edit" heading="게시글 수정" post={selected} onSave={savePost} onCancel={function () { setScreen("detail"); }} busy={busy} />;
  } else if (screen === "delete") {
    content = <DeleteConfirm post={selected} onConfirm={deletePost} onCancel={function () { setScreen("detail"); }} busy={busy} />;
  } else {
    content = <PostDetail post={selected} onEdit={function () { setScreen("edit"); }} onDelete={function () { setScreen("delete"); }} />;
  }

  return (
    <div>
      <div className="actions">
        <button className="primary" onClick={startNew} disabled={busy}>새 게시글</button>
        <button onClick={loadData} disabled={loading || busy}>목록 새로고침</button>
      </div>
      {loading && <p role="status">자료를 불러오고 있습니다.</p>}
      {message && <p className="notice" role="status">{message}</p>}
      <div className="workspace">
        <PostList posts={posts} onSelect={selectPost} />
        {content}
      </div>
    </div>
  );
}
