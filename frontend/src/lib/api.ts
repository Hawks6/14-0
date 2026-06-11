import { DraftSession, Player, SpinResult } from "@/types/draft";
import type { LeagueSeason, LeagueMatch, BallEvent } from "@/types/league";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

function normalizePlayer(player: Player): Player {
  if (!player) return player;
  let role = player.role;
  const upperRole = String(role).toUpperCase();
  if (upperRole === "ALLROUNDER" || upperRole === "ALL-ROUNDER" || upperRole === "AR") {
    role = "AR";
  } else if (upperRole === "BOWLER" || upperRole === "BOWL") {
    role = "BOWL";
  } else if (upperRole === "BATSMAN" || upperRole === "BAT") {
    role = "BAT";
  } else if (upperRole === "WICKETKEEPER" || upperRole === "WK") {
    role = "WK";
  }
  return {
    ...player,
    role,
  };
}

function normalizeDraftSession(session: DraftSession): DraftSession {
  if (!session) return session;
  if (Array.isArray(session.picks)) {
    session.picks = session.picks.map((pick) => {
      if (pick && pick.player) {
        return {
          ...pick,
          player: normalizePlayer(pick.player),
        };
      }
      return pick;
    });
  }
  return session;
}

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
  const session = await apiFetch<DraftSession>("/api/draft/session", { 
    method: "POST",
    body: JSON.stringify({})
  });
  return normalizeDraftSession(session);
}

export async function triggerSpin(sessionId: string): Promise<SpinResult> {
  const result = await apiFetch<SpinResult>(`/api/draft/session/${sessionId}/spin`, {
    method: "POST",
  });
  if (result && Array.isArray(result.players)) {
    result.players = result.players.map(normalizePlayer);
  }
  return result;
}

export async function pickPlayer(
  sessionId: string,
  playerSeasonId: string
): Promise<DraftSession> {
  const session = await apiFetch<DraftSession>(`/api/draft/session/${sessionId}/pick`, {
    method: "POST",
    body: JSON.stringify({ player_season_id: playerSeasonId }),
  });
  return normalizeDraftSession(session);
}

export async function getDraftSession(sessionId: string): Promise<DraftSession> {
  const session = await apiFetch<DraftSession>(`/api/draft/session/${sessionId}`);
  return normalizeDraftSession(session);
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
  const res = await fetch(`${API_BASE}/api/league/${draftSessionId}`, {
    headers: { "Content-Type": "application/json" },
  });
  // 404 means league hasn't been started yet — return empty season
  if (res.status === 404) {
    return { draft_session_id: draftSessionId, matches: [] };
  }
  if (!res.ok) {
    const body = await res.text().catch(() => "");
    throw new Error(`API ${res.status}: ${body || res.statusText}`);
  }
  return res.json();
}

/** Get a single match with full ball-by-ball events */
export async function getMatchDetails(
  matchId: string,
): Promise<LeagueMatch & { events: BallEvent[] }> {
  return apiFetch<LeagueMatch & { events: BallEvent[] }>(
    `/api/league/match/${matchId}`,
  );
}

