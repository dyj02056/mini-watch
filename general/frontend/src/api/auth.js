import { requestJson } from "./client.js";

export function getCurrentUser() {
  return requestJson("/api/auth/me");
}

export function loginUser(username, password, csrfToken) {
  return requestJson("/api/auth/login", "POST", { username, password }, csrfToken);
}

export function logoutUser(csrfToken) {
  return requestJson("/api/auth/logout", "POST", null, csrfToken);
}
