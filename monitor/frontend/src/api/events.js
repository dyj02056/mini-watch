import { requestJson } from "./client.js";

export function getEvents(params = {}) {
  const query = new URLSearchParams();
  if (params.path && params.path.trim()) {
    query.set("path", params.path.trim());
  }
  if (params.statusCode) {
    query.set("status_code", params.statusCode);
  }
  const queryString = query.toString();
  return requestJson(queryString ? `/api/events?${queryString}` : "/api/events");
}