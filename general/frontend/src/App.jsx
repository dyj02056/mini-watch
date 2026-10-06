import { useEffect, useState } from "react";
import { getCurrentUser, loginUser, logoutUser } from "./api/auth.js";
import LoginForm from "./components/LoginForm.jsx";
import Dashboard from "./components/Dashboard.jsx";

export default function App() {
  const [user, setUser] = useState(null);
  const [csrfToken, setCsrfToken] = useState("");
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function restoreSession() {
    try {
      const data = await getCurrentUser();
      setUser(data.user);
      setCsrfToken(data.csrf_token);
    } catch (error) {
      setUser(null);
      setError("서버 연결을 확인하고 새로고침해 주세요.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(function () {
    restoreSession();
  }, []);

  async function login(username, password) {
    setBusy(true);
    setError("");
    try {
      const data = await loginUser(username, password, csrfToken);
      setCsrfToken(data.csrf_token);
      setUser(data.user);
    } catch (error) {
      setError(error.message);
    } finally {
      setBusy(false);
    }
  }

  async function logout() {
    setBusy(true);
    setError("");
    try {
      const data = await logoutUser(csrfToken);
      setCsrfToken(data.csrf_token);
      setUser(data.user);
    } catch (error) {
      setError(error.message);
    } finally {
      setBusy(false);
    }
  }

  function clearError() {
    setError("");
  }

  async function handleError(error) {
    setError(error.message);
    if (error.status === 401) {
      await restoreSession();
    }
  }

  if (loading) {
    return <main className="login-shell"><p role="status">로그인 상태를 확인하고 있습니다.</p></main>;
  }
  if (user === null) {
    return (
      <main className="login-shell">
        <LoginForm title="일반 서비스 로그인" onLogin={login} busy={busy || csrfToken === ""} />
        {error && <p className="error" role="alert">{error}</p>}
      </main>
    );
  }
  return (
    <main className="shell">
      <header className="page-header">
        <div><h1>일반 서비스</h1><p>{user.username}님이 로그인했습니다.</p></div>
        <button onClick={logout} disabled={busy}>로그아웃</button>
      </header>
      {error && <p className="error" role="alert">{error}</p>}
      <Dashboard csrfToken={csrfToken} onError={handleError} onClearError={clearError} />
    </main>
  );
}
