import {
  Player,
  SpinResult,
  DraftPick,
  DraftSession,
  ROSTER_SIZE,
  MAX_OVERSEAS,
  MAX_BUDGET,
} from "@/types/draft";
import type { LeagueSeason, LeagueMatch, BallEvent } from "@/types/league";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const body = await res.text().catch(() => "");
    throw new Error(`API ${res.status}: ${body || res.statusText}`);
  }
  return res.json();
}

// ─── Draft API ──────────────────────────────────────────────────────

export async function createDraftSession(): Promise<DraftSession> {
  return apiFetch<DraftSession>("/api/draft/session", { method: "POST" });
}

export async function triggerSpin(sessionId: string): Promise<SpinResult> {
  return apiFetch<SpinResult>(`/api/draft/session/${sessionId}/spin`, {
    method: "POST",
  });
}

export async function pickPlayer(
  sessionId: string,
  playerSeasonId: string
): Promise<DraftSession> {
  return apiFetch<DraftSession>(`/api/draft/session/${sessionId}/pick`, {
    method: "POST",
    body: JSON.stringify({ player_season_id: playerSeasonId }),
  });
}

export async function getDraftSession(sessionId: string): Promise<DraftSession> {
  return apiFetch<DraftSession>(`/api/draft/session/${sessionId}`);
}

// ─── League API ─────────────────────────────────────────────────────

/** Start a 14-match league season for a completed draft */
export async function startLeague(draftSessionId: string): Promise<LeagueSeason> {
  return apiFetch<LeagueSeason>(`/api/league/start/${draftSessionId}`, {
    method: "POST",
  });
}

/** Get all league matches for a session */
export async function getLeagueMatches(draftSessionId: string): Promise<LeagueSeason> {
  return apiFetch<LeagueSeason>(`/api/league/${draftSessionId}`);
}

/** Get a single match with full ball-by-ball events */
export async function getMatchDetails(
  matchId: string,
): Promise<LeagueMatch & { events: BallEvent[] }> {
  return apiFetch<LeagueMatch & { events: BallEvent[] }>(
    `/api/league/match/${matchId}`,
  );
}
