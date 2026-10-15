import { requestJson } from "./client.js";

export function startDetection() {
  return requestJson("/api/detection/start", "POST", {});
}

export function getDetection(observation) {
  const query = new URLSearchParams({
    after_id: String(observation.after_id),
    started_at: observation.started_at,
  });
  return requestJson(`/api/detection?${query}`);
}
