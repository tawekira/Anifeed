// js/api.js
// Shared fetch wrapper for all pages. Handles base URL, auth token attachment,
// and basic error normalization so individual page scripts don't repeat this logic.

const API_BASE = "";

const TOKEN_KEY = "anifeed_token";

function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

function setToken(token) {
  localStorage.setItem(TOKEN_KEY, token);
}

function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
}

function isLoggedIn() {
  return !!getToken();
}

/**
 * AniDB's CDN blocks direct browser embedding (ORB/CORS). Route those
 * through our own backend proxy endpoint so the browser sees it as
 * same-origin. All other CDNs (which don't have this issue) load directly.
 */
const PROXY_IMAGE_DOMAINS = [
  "anidb.net",
  "anime-planet.com",
];

// Domains that fail even through the proxy (e.g. rate-limited, unreliable) —
// don't attempt to load these at all, just fall back to a placeholder.
const SKIP_IMAGE_DOMAINS = [
  "animenewsnetwork.com",
];

function resolveImageUrl(url) {
  if (!url) return "";

  if (SKIP_IMAGE_DOMAINS.some((domain) => url.includes(domain))) {
    return ""; // caller should fall back to a placeholder when this is empty
  }

  if (PROXY_IMAGE_DOMAINS.some((domain) => url.includes(domain))) {
    return `${API_BASE}/anime/proxy?url=${encodeURIComponent(url)}`;
  }

  return url;
}

/**
 * Core request wrapper.
 * @param {string} path - e.g. "/anime/1" (leading slash required)
 * @param {object} options - fetch options (method, body, etc.)
 * @param {boolean} auth - whether to attach the Authorization header
 */
async function apiRequest(path, options = {}, auth = false) {
  const headers = {
    ...(options.body ? { "Content-Type": "application/json" } : {}),
    ...(options.headers || {}),
  };

  if (auth) {
    const token = getToken();
    if (!token) {
      throw new ApiError(401, "Not logged in");
    }
    headers["Authorization"] = `Bearer ${token}`;
  }

  let response;
  try {
    response = await fetch(`${API_BASE}${path}`, { ...options, headers });
  } catch (err) {
    // Network-level failure (server down, CORS, no connection)
    throw new ApiError(0, "Could not reach the server. Is the backend running?");
  }

  if (!response.ok) {
    let detail = `Request failed (${response.status})`;
    try {
      const data = await response.json();
      if (data.detail) detail = data.detail;
    } catch {
      // response wasn't JSON, keep default message
    }
    throw new ApiError(response.status, detail);
  }

  // Safely handle empty response bodies (e.g. 204 No Content, or a 201
  // whose endpoint doesn't return a body) — don't assume every success
  // status has JSON to parse.
  const text = await response.text();
  if (!text) return null;

  try {
    return JSON.parse(text);
  } catch {
    return null; // body wasn't valid JSON; treat as no data rather than throwing
  }
}

class ApiError extends Error {
  constructor(status, message) {
    super(message);
    this.status = status;
  }
}

// Convenience methods

const api = {
  get: (path, auth = false) => apiRequest(path, { method: "GET" }, auth),

  post: (path, body, auth = false) =>
    apiRequest(path, { method: "POST", body: JSON.stringify(body) }, auth),

  del: (path, auth = false) => apiRequest(path, { method: "DELETE" }, auth),

  // Login uses x-www-form-urlencoded, not JSON (OAuth2PasswordRequestForm requirement)
  login: async (username, password) => {
    const body = new URLSearchParams();
    body.append("username", username);
    body.append("password", password);

    const response = await fetch(`${API_BASE}/auth/token`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body,
    });

    if (!response.ok) {
      throw new ApiError(response.status, "Incorrect username or password");
    }

    return response.json(); // { access_token, token_type }
  },
};