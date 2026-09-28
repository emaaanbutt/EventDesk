const TOKEN_KEY = "eventdesk.tokens";
let refreshPromise = null;

export class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.status = status;
  }
}

export function getTokens() {
  try {
    return JSON.parse(localStorage.getItem(TOKEN_KEY));
  } catch {
    return null;
  }
}

export function setTokens(tokens) {
  if (tokens) localStorage.setItem(TOKEN_KEY, JSON.stringify(tokens));
  else localStorage.removeItem(TOKEN_KEY);
  window.dispatchEvent(new Event("eventdesk:auth"));
}

function errorMessage(detail) {
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail))
    return detail.map((item) => item.msg || "Invalid input").join(" · ");
  return "Something went wrong. Please try again.";
}

async function parseResponse(response) {
  if (response.status === 204) return null;
  const data = await response.json().catch(() => null);
  if (!response.ok)
    throw new ApiError(errorMessage(data?.detail), response.status);
  return data;
}

async function refreshAccessToken() {
  if (refreshPromise) return refreshPromise;
  refreshPromise = (async () => {
    const token = getTokens()?.refresh_token;
    if (!token) throw new ApiError("Please sign in again.", 401);
    const response = await fetch("/api/auth/refresh", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: token }),
    });
    const next = await parseResponse(response);
    setTokens(next);
    return next.access_token;
  })();
  try {
    return await refreshPromise;
  } catch (error) {
    setTokens(null);
    throw error;
  } finally {
    refreshPromise = null;
  }
}

export async function api(
  path,
  { method = "GET", body, auth = true, ...options } = {},
) {
  const send = (token) =>
    fetch(`/api${path}`, {
      method,
      ...options,
      headers: {
        ...(body !== undefined ? { "Content-Type": "application/json" } : {}),
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...options.headers,
      },
      ...(body !== undefined ? { body: JSON.stringify(body) } : {}),
    });
  let response;
  try {
    response = await send(auth ? getTokens()?.access_token : null);
    if (response.status === 401 && auth && getTokens()?.refresh_token) {
      response = await send(await refreshAccessToken());
    }
  } catch (error) {
    if (error instanceof ApiError) throw error;
    throw new ApiError(
      "Cannot reach the API. Check that FastAPI is running.",
      0,
    );
  }
  return parseResponse(response);
}

export function query(path, params = {}) {
  const search = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== "" && value !== null && value !== undefined)
      search.set(key, String(value));
  });
  return `${path}${search.size ? `?${search}` : ""}`;
}

export function openSocket(path) {
  const scheme = window.location.protocol === "https:" ? "wss" : "ws";
  return new WebSocket(`${scheme}://${window.location.host}${path}`);
}
