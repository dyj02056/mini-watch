let currentCsrfToken = "";

export function setCsrfToken(token) {
  currentCsrfToken = token || "";
}

export function getCsrfToken() {
  return currentCsrfToken;
}

export async function requestJson(path, method = "GET", data = null) {
  const options = {
    method: method,
    credentials: "same-origin",
    headers: {
      "Content-Type": "application/json",
    },
  };
  if (currentCsrfToken && method !== "GET" && method !== "HEAD") {
    options.headers["X-CSRF-Token"] = currentCsrfToken;
  }
  if (data !== null) {
    options.body = JSON.stringify(data);
  }
  const response = await fetch(path, options);
  let result;
  try {
    result = await response.json();
  } catch {
    result = {};
  }
  if (result.csrf_token) {
    setCsrfToken(result.csrf_token);
  }
  if (!response.ok) {
    throw new Error(result.error || `요청 처리에 실패했습니다 (${response.status})`);
  }
  return result;
}