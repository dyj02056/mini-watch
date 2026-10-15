/**
 * Next.js Route Handler 프록시
 * 브라우저의 /api/... 요청을 감시 Flask(MONITOR_API_URL)로 전달합니다.
 * Cookie, X-CSRF-Token, Set-Cookie, 상태 코드를 양방향으로 전달합니다.
 * MONITOR_API_URL은 서버 전용 환경 변수 — 브라우저 코드나 NEXT_PUBLIC_*에 노출하지 않습니다.
 */

const MONITOR_API_URL = process.env.MONITOR_API_URL;

async function proxyRequest(request, { params }) {
  if (!MONITOR_API_URL) {
    return Response.json(
      { error: "감시 API 주소(MONITOR_API_URL)가 설정되지 않았습니다." },
      { status: 503 }
    );
  }

  const pathSegments = (await params).path;
  const resource = pathSegments.join("/");
  const method = request.method;
  const allowed =
    (resource === "auth/me" && method === "GET") ||
    ((resource === "auth/login" || resource === "auth/logout") && method === "POST") ||
    (resource === "events" && method === "GET") ||
    ((resource === "analysis" || resource === "analysis/raw" || resource === "detection" || resource === "sentry-test") && method === "GET") ||
    ((resource === "analysis/start" || resource === "detection/start") && method === "POST") ||
    (resource === "notes" && ["GET", "POST"].includes(method)) ||
    (/^notes\/\d+$/.test(resource) && ["GET", "PUT", "DELETE"].includes(method));
  if (!allowed) {
    return Response.json({ error: "지원하지 않는 API 요청입니다." }, { status: 404 });
  }
  const path = "/api/" + pathSegments.join("/");
  const search = new URL(request.url).search;
  const baseUrl = MONITOR_API_URL.replace(/\/api\/?$/, "").replace(/\/$/, "");
  const targetUrl = baseUrl + path + search;

  // 전달할 요청 헤더 구성 (Cookie, X-CSRF-Token 포함)
  const forwardHeaders = new Headers();
  const cookie = request.headers.get("cookie");
  if (cookie) forwardHeaders.set("cookie", cookie);
  const csrfToken = request.headers.get("x-csrf-token");
  if (csrfToken) forwardHeaders.set("x-csrf-token", csrfToken);
  const contentType = request.headers.get("content-type");
  if (contentType) forwardHeaders.set("content-type", contentType);

  let body = null;
  if (request.method !== "GET" && request.method !== "HEAD") {
    body = await request.arrayBuffer();
  }

  let upstream;
  try {
    upstream = await fetch(targetUrl, {
      method: request.method,
      headers: forwardHeaders,
      body: body,
    });
  } catch (err) {
    console.error("[proxy] 감시 Flask 연결 실패:", err.message);
    return Response.json(
      { error: "감시 서비스에 연결할 수 없습니다. 잠시 후 다시 시도해 주세요." },
      { status: 502 }
    );
  }

  // 응답 헤더 구성 (Set-Cookie, 상태 코드 전달)
  const responseHeaders = new Headers();
  const setCookie = upstream.headers.get("set-cookie");
  if (setCookie) responseHeaders.set("set-cookie", setCookie);
  responseHeaders.set("content-type", upstream.headers.get("content-type") || "application/json");

  const responseBody = await upstream.arrayBuffer();
  return new Response(responseBody, {
    status: upstream.status,
    headers: responseHeaders,
  });
}

export const GET = proxyRequest;
export const POST = proxyRequest;
export const PUT = proxyRequest;
export const PATCH = proxyRequest;
export const DELETE = proxyRequest;

