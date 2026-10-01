import type { DropStatus } from "./types";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function postJson<T>(path: string, body?: unknown): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: body ? { "Content-Type": "application/json" } : undefined,
    body: body ? JSON.stringify(body) : undefined,
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(data.detail || `Request failed (${res.status})`);
  }
  return data as T;
}

export async function fetchStatus(userId: string): Promise<DropStatus> {
  const res = await fetch(
    `${API_BASE}/status?user_id=${encodeURIComponent(userId)}`,
  );
  if (!res.ok) throw new Error("Failed to fetch status");
  return res.json();
}

export const buySneaker = (userId: string) =>
  postJson<{ ok: boolean; hold_id?: number; position?: number }>("/buy", {
    user_id: userId,
  });

export const paySneaker = (holdId: number) =>
  postJson<{ ok: boolean; payment_id: number }>("/pay", { hold_id: holdId });

export const resetDrop = () =>
  postJson<{ ok: boolean; message: string }>("/reset");
