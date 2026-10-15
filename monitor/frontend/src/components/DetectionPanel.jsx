import { useState } from "react";
import { getDetection, startDetection } from "../api/detection.js";

function displayTime(value) {
  return new Date(value).toLocaleString("ko-KR", { hour12: false });
}

export default function DetectionPanel(props) {
  const [observation, setObservation] = useState(() => {
    try {
      return JSON.parse(window.localStorage.getItem("mini-watch-detection-observation")) || null;
    } catch {
      return null;
    }
  });
  const [report, setReport] = useState(null);
  const [busy, setBusy] = useState(false);

  async function begin() {
    setBusy(true);
    props.onClearError();
    try {
      const result = await startDetection();
      window.localStorage.setItem("mini-watch-detection-observation", JSON.stringify(result));
      setObservation(result);
      setReport(null);
    } catch (error) {
      props.onError(error);
    } finally {
      setBusy(false);
    }
  }

  async function refresh() {
    if (!observation) return;
    setBusy(true);
    props.onClearError();
    try {
      setReport(await getDetection(observation));
    } catch (error) {
      props.onError(error);
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="panel detection-panel" aria-busy={busy}>
      <div className="detection-heading-row">
        <div><p className="muted">Day4 · 로그에서 경고로</p><h2>반복 로그인 실패 탐지</h2></div>
        <span className="detection-caution">수업용 기준 · 공격 확정 아님</span>
      </div>
      <p>같은 입력 계정으로 60초 안에 로그인 실패가 3회 이상 발생하면 근거 기록과 함께 표시합니다.</p>
      <ol className="detection-steps">
        <li>새 관찰을 시작합니다.</li><li>일반 사이트에서 같은 아이디로 로그인을 반복해 실패시킵니다.</li>
        <li>탐지 새로고침을 눌러 결과를 확인합니다.</li>
      </ol>
      <div className="actions">
        <button className="primary" onClick={begin} disabled={busy}>새 관찰 시작</button>
        <button onClick={refresh} disabled={busy || !observation}>탐지 새로고침</button>
        <a href="http://localhost:8081/login" target="_blank" rel="noreferrer">일반 사이트 열기</a>
      </div>
      {observation && <p role="status">관찰 시작: {displayTime(observation.started_at)}</p>}
      {report && <>
        {report.counts.length === 0 && <p>최근 60초 동안 로그인 실패가 없습니다.</p>}
        {report.counts.map((item) => <p key={item.attempted_username}>{item.attempted_username}: 최근 60초 실패 {item.count}회</p>)}
        {report.alerts.length === 0 && <p>현재 관찰에서 기준을 충족한 경고가 없습니다.</p>}
        {report.alerts.map((alert) => <article className="detection-alert" key={alert.attempted_username}>
          <h3>{alert.attempted_username} · 반복 로그인 실패</h3>
          <p>관찰 중 60초 안에 실패 {report.rule.threshold}회 이상 발생했습니다. 경고 근거:</p>
          <ol className="detection-evidence-list">{alert.events.map((event) => <li key={event.id}>
            <time dateTime={event.occurred_at}>{displayTime(event.occurred_at)}</time>
            <span>{event.status_code} · <code>{event.method} {event.path}</code> · 근거 ID {event.id}</span>
          </li>)}</ol>
        </article>)}
      </>}
    </section>
  );
}
