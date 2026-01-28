/**
 * API Client
 * Functions for fetching data from the backend API.
 */

import { API_BASE_URL } from './constants';
import type {
  GlobalStatsResponse,
  UserStatsResponse,
  DistributionHistoryItem,
  LeaderboardEntry,
  PoolStatusResponse,
  DistributionItem,
  ApiError,
} from '@/types/api';

// ===========================================
// Error Handling
// ===========================================

/**
 * Extract error message from various error types
 */
export function getErrorMessage(error: unknown): string {
  if (error instanceof Error) {
    return error.message;
  }
  if (typeof error === 'object' && error !== null) {
    if ('message' in error && typeof error.message === 'string') {
      return error.message;
    }
    if ('detail' in error && typeof error.detail === 'string') {
      return error.detail;
    }
  }
  if (typeof error === 'string') {
    return error;
  }
  return 'An unknown error occurred';
}

/**
 * Fetch wrapper with error handling
 */
async function fetchApi<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options?.headers as Record<string, string>),
  };

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let errorMessage = `HTTP ${response.status}`;
    try {
      const errorData = await response.json() as { detail?: string; message?: string };
      errorMessage = errorData.detail || errorData.message || errorMessage;
    } catch {
      // Ignore JSON parse errors
    }
    const error: ApiError = {
      status: response.status,
      message: errorMessage,
    };
    throw error;
  }

  return response.json() as Promise<T>;
}

// ===========================================
// API Functions
// ===========================================

/**
 * Get global statistics
 */
export async function getGlobalStats(): Promise<GlobalStatsResponse> {
  return fetchApi<GlobalStatsResponse>('/api/stats');
}

/**
 * Get user statistics by wallet address
 */
export async function getUserStats(wallet: string): Promise<UserStatsResponse> {
  return fetchApi<UserStatsResponse>(`/api/user/${wallet}`);
}

/**
 * Get user distribution history
 */
export async function getUserHistory(
  wallet: string,
  limit = 10
): Promise<DistributionHistoryItem[]> {
  return fetchApi<DistributionHistoryItem[]>(
    `/api/user/${wallet}/history?limit=${limit}`
  );
}

/**
 * Get leaderboard entries
 */
export async function getLeaderboard(limit = 100): Promise<LeaderboardEntry[]> {
  return fetchApi<LeaderboardEntry[]>(`/api/leaderboard?limit=${limit}`);
}

/**
 * Get pool status
 */
export async function getPoolStatus(): Promise<PoolStatusResponse> {
  return fetchApi<PoolStatusResponse>('/api/pool');
}

/**
 * Get distribution history
 */
export async function getDistributions(
  limit = 10,
  offset = 0
): Promise<DistributionItem[]> {
  return fetchApi<DistributionItem[]>(
    `/api/distributions?limit=${limit}&offset=${offset}`
  );
}
