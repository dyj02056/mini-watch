import { useState } from "react";

function LoginForm(props) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");

  function changeUsername(event) {
    setUsername(event.target.value);
  }

  function changePassword(event) {
    setPassword(event.target.value);
  }

  function handleSubmit(event) {
    event.preventDefault();
    if (username.trim() === "" || password === "") {
      setMessage("아이디와 비밀번호를 입력해 주세요.");
      return;
    }
    setMessage(username + "의 입력을 확인했습니다. 아직 서버에 보내지는 않았습니다.");
  }

  return (
    <section className="panel">
      <h1>{props.title}</h1>
      <form onSubmit={handleSubmit}>
        <label>아이디<input value={username} onChange={changeUsername} autoComplete="username" /></label>
        <label>비밀번호<input type="password" value={password} onChange={changePassword} autoComplete="current-password" /></label>
        <button className="primary" type="submit">입력 확인</button>
      </form>
      <p className="notice" role="status">{message}</p>
    </section>
  );
}

export default function App() {
  return (
    <main className="login-shell">
      <LoginForm title="감시 서비스 로그인" />
    </main>
  );
}