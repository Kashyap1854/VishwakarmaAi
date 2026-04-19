// api.js — all fetch calls to the FastAPI backend

const BASE = "/api";

function getToken() {
  return localStorage.getItem("vk_token") || "";
}

function authHeaders() {
  return {
    Authorization: `Bearer ${getToken()}`,
  };
}

// ── Auth ──────────────────────────────────────────────────────────────────────
export async function apiRegister(name, email, password) {
  const res = await fetch(`${BASE}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, email, password }),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Registration failed");
  return data; // { access_token, user }
}

export async function apiLogin(email, password) {
  const res = await fetch(`${BASE}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Login failed");
  return data; // { access_token, user }
}

export async function apiMe() {
  const res = await fetch(`${BASE}/auth/me`, {
    headers: authHeaders(),
  });
  if (!res.ok) throw new Error("Not authenticated");
  return res.json();
}

// ── Analysis ──────────────────────────────────────────────────────────────────
export async function apiAnalyze(file) {
  const form = new FormData();
  form.append("image", file);
  const res = await fetch(`${BASE}/analyze`, {
    method: "POST",
    headers: authHeaders(),
    body: form,
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Analysis failed");
  return data;
}

// ── History ───────────────────────────────────────────────────────────────────
export async function apiGetHistory(skip = 0, limit = 20) {
  const res = await fetch(`${BASE}/history?skip=${skip}&limit=${limit}`, {
    headers: authHeaders(),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Failed to load history");
  return data;
}

export async function apiGetAnalysis(id) {
  const res = await fetch(`${BASE}/history/${id}`, {
    headers: authHeaders(),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Failed to load analysis");
  return data;
}

export async function apiDeleteAnalysis(id) {
  const res = await fetch(`${BASE}/history/${id}`, {
    method: "DELETE",
    headers: authHeaders(),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Delete failed");
  return data;
}

export async function apiClearHistory() {
  const res = await fetch(`${BASE}/history`, {
    method: "DELETE",
    headers: authHeaders(),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Clear failed");
  return data;
}

// ── Monuments ─────────────────────────────────────────────────────────────────
export async function apiGetMonuments(style = "", search = "") {
  const params = new URLSearchParams();
  if (style)  params.set("style",  style);
  if (search) params.set("search", search);
  const res = await fetch(`${BASE}/monuments?${params}`);
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Failed to load monuments");
  return data;
}
