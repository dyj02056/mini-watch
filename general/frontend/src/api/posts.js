import { requestJson } from "./client.js";

export function getPosts() {
  return requestJson("/api/posts");
}

export function getPost(id) {
  return requestJson("/api/posts/" + id);
}

export function createPost(title, body, csrfToken) {
  return requestJson("/api/posts", "POST", { title, body }, csrfToken);
}

export function updatePost(id, title, body, csrfToken) {
  return requestJson("/api/posts/" + id, "PUT", { title, body }, csrfToken);
}

export function removePost(id, csrfToken) {
  return requestJson("/api/posts/" + id, "DELETE", null, csrfToken);
}
