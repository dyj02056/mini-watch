export async function requestJson(path, method = "GET", data = null) {
  const upperMethod = method.toUpperCase();
  const headers = { "Content-Type": "application/json" };
  if (["POST", "PUT", "PATCH", "DELETE"].includes(upperMethod)) {
    const sessionResponse = await fetch("/api/auth/me");
    const sessionData = await sessionResponse.json();
    headers["X-CSRF-Token"] = sessionData.csrf_token;
  }
  const options = {
    method: method,
    headers,
  };
  if (data !== null) {
    options.body = JSON.stringify(data);
  }
  const response = await fetch(path, options);
  const result = await response.json();
  if (!response.ok) {
    throw new Error(result.error);
  }
  return result;
}
