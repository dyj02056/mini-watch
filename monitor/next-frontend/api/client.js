export async function requestJson(path, method = "GET", data = null) {
  const options = {
    method: method,
    headers: { "Content-Type": "application/json" },
  };
  if (data !== null) {
    options.body = JSON.stringify(data);
  }

  const response = await fetch(path, options);
  let result;
  try {
    result = await response.json();
  } catch {
    throw new Error("API 응답을 읽을 수 없습니다. Flask 서버와 연결 주소를 확인해 주세요.");
  }
  if (!response.ok) {
    throw new Error(result.error || "요청을 처리하지 못했습니다.");
  }
  return result;
}