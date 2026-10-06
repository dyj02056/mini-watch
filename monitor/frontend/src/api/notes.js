import { requestJson } from "./client.js";

export function getNotes() {
  return requestJson("/api/notes");
}

export function getNote(id) {
  return requestJson("/api/notes/" + id);
}

export function createNote(title, body, csrfToken) {
  return requestJson("/api/notes", "POST", { title, body }, csrfToken);
}

export function updateNote(id, title, body, csrfToken) {
  return requestJson("/api/notes/" + id, "PUT", { title, body }, csrfToken);
}

export function removeNote(id, csrfToken) {
  return requestJson("/api/notes/" + id, "DELETE", null, csrfToken);
}
