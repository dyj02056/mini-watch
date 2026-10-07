import { requestJson } from "./client.js";

export function getNotes() {
  return requestJson("/api/notes");
}

export function getNote(id) {
  return requestJson("/api/notes/" + id);
}

export function createNote(title, body, status = "확인 전") {
  return requestJson("/api/notes", "POST", { title, body, status });
}

export function updateNote(id, title, body, status = "확인 전") {
  return requestJson("/api/notes/" + id, "PUT", { title, body, status });
}

export function removeNote(id) {
  return requestJson("/api/notes/" + id, "DELETE", null);
}