import { useEffect, useState } from "react";
import { loginUser, getMe, logoutUser } from "./api/auth.js";
import LoginForm from "./components/LoginForm.jsx";
import Dashboard from "./components/Dashboard.jsx";

export default function App() {
  const [user, setUser] = useState(null);
  const [checkingAuth, setCheckingAuth] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  useEffect(function () {
    async function restoreSession() {
      try {
        const data = await getMe();
        if (data && data.user) {
          setUser(data.user);
        }
      } catch (err) {
        // 비로그인 상태일 때는 조용히 로그인 폼 표시
      } finally {
        setCheckingAuth(false);
      }
    }
    restoreSession();
  }, []);

  async function login(username, password) {
    setBusy(true);
    setError("");
    try {
      const data = await loginUser(username, password);
      setUser(data.user);
    } catch (error) {
      setError(error.message);
    } finally {
      setBusy(false);
    }
  }

  async function logout() {
    setBusy(true);
    try {
      await logoutUser();
    } catch {
      // 로그아웃 요청 실패 시에도 클라이언트 상태는 초기화
    } finally {
      setUser(null);
      setError("");
      setBusy(false);
    }
  }

  function clearError() {
    setError("");
  }

  function handleError(error) {
    setError(error.message);
  }

  if (checkingAuth) {
    return (
      <main className="login-shell">
        <p role="status">인증 상태를 확인하고 있습니다...</p>
      </main>
    );
  }

  if (user === null) {
    return (
      <main className="login-shell">
        <LoginForm title="감시 서비스 로그인" onLogin={login} busy={busy} />
        {error && <p className="error" role="alert">{error}</p>}
      </main>
    );
  }

  return (
    <main className="shell">
      <header className="page-header">
        <div>
          <h1>감시 서비스</h1>
          <p>{user.username}님이 로그인했습니다.</p>
        </div>
        <button onClick={logout} disabled={busy}>로그아웃</button>
      </header>
      {error && <p className="error" role="alert">{error}</p>}
      <Dashboard onError={handleError} onClearError={clearError} />
    </main>
  );
}