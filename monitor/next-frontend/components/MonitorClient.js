"use client";
import { useCallback, useEffect, useState } from "react";
import { requestJson } from "../api/client";
import NotesClient from "./NotesClient";
import DetectionClient from "./DetectionClient";
import AnalysisClient from "./AnalysisClient";

export default function MonitorClient() {
  const [user, setUser] = useState(null);
  const [username, setUsername] = useState("class-operator");
  const [password, setPassword] = useState("");
  const [events, setEvents] = useState([]);
  const [threshold, setThreshold] = useState(10);
  const [observation, setObservation] = useState(null);
  const [report, setReport] = useState(null);
  const [message, setMessage] = useState("");
  const checkSession = useCallback(async () => {
    try {
      const result = await requestJson("/api/auth/me");
      setUser(result.user);
      setMessage(result.user ? "로그인 상태를 확인했습니다." : "로그인해 주세요.");
    } catch (error) { setMessage(error.message); }
  }, []);
  useEffect(() => {
    checkSession();
  }, [checkSession]);
  async function login(event) {
    event.preventDefault();
    try {
      const result = await requestJson("/api/auth/login", "POST", { username, password });
      setUser(result.user);
      setPassword("");
      setMessage("로그인했습니다.");
    } catch (error) { setMessage(error.message); }
  }
  async function logout() {
    try {
      await requestJson("/api/auth/logout", "POST");
      setUser(null);
      setEvents([]);
      setObservation(null);
      setReport(null);
      setMessage("로그아웃했습니다.");
    } catch (error) { setMessage(error.message); }
  }
  async function loadEvents() {
    try {
      const result = await requestJson("/api/events");
      setEvents(result.events);
      setMessage("요청 기록을 불러왔습니다.");
    } catch (error) { setMessage(error.message); }
  }
  async function startObservation() {
    try {
      const result = await requestJson("/api/analysis/start", "POST", {});
      setObservation({ after_id: result.after_id, reference_time: null });
      setReport(null);
      setMessage(`새 관찰을 시작했습니다. 시작 ID: ${result.after_id}`);
    } catch (error) { setMessage(error.message); }
  }
  async function loadAnalysis() {
    if (!observation) { setMessage("먼저 새 관찰을 시작해 주세요."); return; }
    try {
      const params = new URLSearchParams({ after_id: observation.after_id, threshold: String(threshold) });
      if (observation.reference_time) params.set("reference_time", observation.reference_time);
      const result = await requestJson(`/api/analysis?${params}`);
      setObservation({ after_id: result.after_id, reference_time: result.reference_time });
      setReport(result.cards[0]);
      setMessage("분석 결과를 불러왔습니다. 기준을 바꾸면 같은 관찰 구간을 다시 계산합니다.");
    } catch (error) { setMessage(error.message); }
  }
  return (
    <main>
      <h1>감시 서비스</h1>
      <button onClick={checkSession}>현재 로그인 확인</button>
      <p role="status">{message}</p>
      {!user ? (
        <form onSubmit={login}>
          <p>수업 계정 class-operator / classroom1234!를 사용하거나 기존 operator 계정을 이용하세요.</p>
          <label>아이디<input value={username} onChange={e => setUsername(e.target.value)} /></label>
          <label>비밀번호<input type="password" value={password} onChange={e => setPassword(e.target.value)} /></label>
          <button>로그인</button>
        </form>
      ) : (
        <>
          <p>{user.username} 사용자</p>
          <button onClick={logout}>로그아웃</button>
          <DetectionClient />
          <details className="detection-log-review">
            <summary>앱·Nginx 원본 로그 함께 보기</summary>
            <AnalysisClient />
          </details>
          <h2>요청 기록</h2>
          <button onClick={loadEvents}>기록 불러오기</button>
          <div style={{overflowX:"auto"}}>
            <table><thead><tr><th>종류</th><th>방법</th><th>경로</th><th>상태</th><th>입력 계정</th></tr></thead>
              <tbody>{events.map(item => <tr key={item.id}><td>{item.event_type}</td><td>{item.method}</td><td>{item.path}</td><td>{item.status_code}</td><td>{item.attempted_username || "—"}</td></tr>)}</tbody>
            </table>
          </div>
          <section className="panel" aria-labelledby="analysis-title">
            <h2 id="analysis-title">HTTP 관찰 분석</h2>
            <p>새 관찰은 현재 마지막 기록 ID를 경계로 설정합니다. 첫 결과 조회 후 기준 비교에 같은 시각을 사용합니다.</p>
            <div className="actions">
              <button onClick={startObservation}>새 관찰 시작</button>
              <label>기준값<input type="number" min="1" max="10000" value={threshold} onChange={e => setThreshold(e.target.value)} /></label>
              <button onClick={loadAnalysis} disabled={!observation}>결과 불러오기</button>
            </div>
            {observation && <p>after_id: {observation.after_id} · 기준시각: {observation.reference_time || "첫 결과 조회 시 설정"}</p>}
            {report && <article>
              <h3>{report.verdict}</h3>
              <p>관찰값 {report.observed} · 기준 {report.threshold}</p>
              <p>{report.reason}</p>
              <p>조회 ID: {report.view_ids.join(", ") || "없음"}</p>
              <p>뒤따른 404 ID: {report.error_ids.join(", ") || "없음"}</p>
              <h3>근거 행 ({report.records.length})</h3>
              <div style={{overflowX:"auto"}}><table><thead><tr><th>ID</th><th>수신시각</th><th>방법</th><th>경로</th><th>상태</th><th>종류</th></tr></thead>
                <tbody>{report.records.map(row => <tr key={row.id}><td>{row.id}</td><td>{row.received_at}</td><td>{row.method}</td><td>{row.path}</td><td>{row.status_code}</td><td>{row.kind}</td></tr>)}</tbody>
              </table></div>
            </article>}
          </section>
          <h2>관찰 메모</h2>
          <NotesClient />
        </>
      )}
    </main>
  );
}
