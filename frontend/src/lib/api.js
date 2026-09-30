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

const FIELD_LABELS = {
  date_from: "From date",
  date_to: "To date",
  starts_at: "Start date and time",
  ends_at: "End date and time",
  ticket_price: "Ticket price",
  total_tickets: "Total tickets",
  category_id: "Category",
  tag_id: "Tag",
  tag_ids: "Tags",
  event_id: "Event",
  refresh_token: "Refresh token",
  new_password: "New password",
  current_password: "Current password",
  page_size: "Page size",
  is_read: "Read status",
};

function fieldLabel(name) {
  return FIELD_LABELS[name] || name.replaceAll("_", " ").replace(/^./, (letter) => letter.toUpperCase());
}

function friendlyText(message) {
  const clean = message.replace(/^Value error,\s*/i, "").replace(/\s*\[type=.*$/i, "");
  if (/date_from must be before or equal to date_to/i.test(clean))
    return "From date must be on or before To date.";
  if (/Only published events can be booked/i.test(clean))
    return "Booking is closed for this event.";
  return clean.replace(/\b[a-z]+(?:_[a-z]+)+\b/g, (name) => fieldLabel(name));
}

function validationMessage(item) {
  const name = [...(item.loc || [])].reverse().find((part) => typeof part === "string" && !["body", "query", "path"].includes(part));
  const label = name ? fieldLabel(name) : "This information";
  const limit = item.ctx?.min_length ?? item.ctx?.max_length ?? item.ctx?.gt ?? item.ctx?.ge ?? item.ctx?.lt ?? item.ctx?.le;
  switch (item.type) {
    case "missing": return `${label} is required.`;
    case "string_too_short": return item.ctx?.min_length === 1 ? `${label} cannot be empty.` : `${label} must be at least ${limit} characters.`;
    case "string_too_long": return `${label} must be ${limit} characters or fewer.`;
    case "greater_than": return `${label} must be greater than ${limit}.`;
    case "greater_than_equal": return `${label} must be at least ${limit}.`;
    case "less_than": return `${label} must be less than ${limit}.`;
    case "less_than_equal": return `${label} must be at most ${limit}.`;
    case "int_parsing": case "int_type": return `${label} must be a whole number.`;
    case "float_parsing": case "decimal_parsing": return `${label} must be a number.`;
    case "string_type": return `${label} must be text.`;
    case "bool_parsing": case "bool_type": return `${label} must be yes or no.`;
    case "list_type": return `Please check ${label.toLowerCase()}.`;
    case "literal_error": case "enum": return `Choose a valid ${label.toLowerCase()}.`;
    case "uuid_parsing": case "uuid_type": return `Please choose a valid ${label.toLowerCase()}.`;
    case "datetime_parsing": case "datetime_from_date_parsing": case "datetime_object_invalid": return `Enter a valid ${label.toLowerCase()}.`;
    case "decimal_max_digits": case "decimal_max_places": return `${label} has too many digits.`;
    case "extra_forbidden": return `${label} is not supported.`;
    default: return friendlyText(item.msg || `Please check ${label.toLowerCase()}.`);
  }
}

export function errorMessage(detail) {
  if (typeof detail === "string") return friendlyText(detail);
  if (Array.isArray(detail))
    return detail.map(validationMessage).join(" · ");
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
      "We couldn't connect. Please check your connection and try again.",
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
