import { requestJson } from "./client.js";

export function loginUser(username, password) {
  return requestJson("/api/auth/login", "POST", { username, password });
}

export function getMe() {
  return requestJson("/api/auth/me");
}

export function logoutUser() {
  return requestJson("/api/auth/logout", "POST", {});
}