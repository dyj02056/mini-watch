import { useState } from "react";

export default function EventList(props) {
  const [inputPath, setInputPath] = useState(props.pathFilter || "");
  const [inputStatus, setInputStatus] = useState(props.statusCodeFilter || "");

  function handleFilterSubmit(e) {
    e.preventDefault();
    props.onApplyFilter({ path: inputPath, statusCode: inputStatus });
  }

  function handleReset() {
    setInputPath("");
    setInputStatus("");
    props.onApplyFilter({ path: "", statusCode: "" });
  }

  const totalCount = props.events.length;
  const errorCount = props.events.filter(function (e) {
    return e.status_code >= 400;
  }).length;

  return (
    <section className="panel">
      <h2>최근 요청 기록</h2>
      <p className="muted">
        일반 서비스가 보낸 최근 50건 기록입니다. (오류 기준: 상태 코드 400 이상)
      </p>

      {/* 건수 요약 통계 카드 */}
      <div
        style={{
          display: "flex",
          gap: "16px",
          margin: "12px 0 16px 0",
        }}
      >
        <div
          style={{
            flex: 1,
            padding: "12px 16px",
            background: "#f1f5f9",
            borderRadius: "6px",
            border: "1px solid #cbd5e1",
          }}
        >
          <span style={{ fontSize: "0.85rem", color: "#64748b" }}>조회된 전체 요청</span>
          <p
            style={{
              margin: "4px 0 0 0",
              fontSize: "1.4rem",
              fontWeight: "bold",
              color: "#0f172a",
            }}
          >
            {totalCount}건
          </p>
        </div>
        <div
          style={{
            flex: 1,
            padding: "12px 16px",
            background: errorCount > 0 ? "#fef2f2" : "#f0fdf4",
            borderRadius: "6px",
            border: `1px solid ${errorCount > 0 ? "#fecaca" : "#bbf7d0"}`,
          }}
        >
          <span
            style={{
              fontSize: "0.85rem",
              color: errorCount > 0 ? "#b91c1c" : "#15803d",
            }}
          >
            오류 요청 (4xx / 5xx)
          </span>
          <p
            style={{
              margin: "4px 0 0 0",
              fontSize: "1.4rem",
              fontWeight: "bold",
              color: errorCount > 0 ? "#dc2626" : "#16a34a",
            }}
          >
            {errorCount}건
          </p>
        </div>
      </div>

      {/* 필터 폼 */}
      <form
        onSubmit={handleFilterSubmit}
        style={{
          display: "flex",
          gap: "8px",
          alignItems: "center",
          flexWrap: "wrap",
          marginBottom: "16px",
          padding: "10px",
          background: "#f8fafc",
          borderRadius: "6px",
        }}
      >
        <label style={{ display: "flex", alignItems: "center", gap: "6px", margin: 0 }}>
          <span>경로 검색:</span>
          <input
            type="text"
            placeholder="예: /board, /login"
            value={inputPath}
            onChange={function (e) {
              setInputPath(e.target.value);
            }}
            style={{ padding: "6px 10px", width: "160px" }}
          />
        </label>
        <label style={{ display: "flex", alignItems: "center", gap: "6px", margin: 0 }}>
          <span>상태 코드:</span>
          <select
            value={inputStatus}
            onChange={function (e) {
              setInputStatus(e.target.value);
            }}
            style={{ padding: "6px 10px" }}
          >
            <option value="">전체 상태</option>
            <option value="200">200 (성공)</option>
            <option value="201">201 (생성됨)</option>
            <option value="302">302 (리다이렉트)</option>
            <option value="400">400 (잘못된 요청)</option>
            <option value="401">401 (인증 필요)</option>
            <option value="403">403 (권한 없음)</option>
            <option value="404">404 (찾을 수 없음)</option>
            <option value="500">500 (서버 오류)</option>
          </select>
        </label>
        <button type="submit" className="primary" style={{ padding: "6px 12px" }}>
          필터 적용
        </button>
        {(inputPath || inputStatus || props.pathFilter || props.statusCodeFilter) && (
          <button type="button" onClick={handleReset} style={{ padding: "6px 12px" }}>
            필터 초기화
          </button>
        )}
      </form>

      {props.events.length === 0 && (
        <p>조건에 맞는 요청 기록이 없습니다. 일반 서비스에 접속하거나 필터를 초기화해 보세요.</p>
      )}

      <div className="table-scroll">
        <table>
          <thead>
            <tr>
              <th>시각</th>
              <th>메서드</th>
              <th>경로</th>
              <th>상태 코드</th>
              <th>분류</th>
            </tr>
          </thead>
          <tbody>
            {props.events.map(function (event) {
              const isError = event.status_code >= 400;
              return (
                <tr key={event.id} style={isError ? { backgroundColor: "#fff5f5" } : {}}>
                  <td>{event.occurred_at}</td>
                  <td>{event.method}</td>
                  <td>{event.path}</td>
                  <td style={isError ? { color: "#dc2626", fontWeight: "bold" } : {}}>
                    {event.status_code}
                  </td>
                  <td>{event.event_type}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </section>
  );
}