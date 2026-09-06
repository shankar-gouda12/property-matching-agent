'use client';

import React, { FormEvent, useEffect, useState } from 'react';
import SearchFilters from './SearchFilters';
import PropertyResults from './PropertyResults';
import { FilterOptions, PropertyMatch } from './interfaces';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://127.0.0.1:8000/api';
const LIVE_INVENTORY_POLL_MS = 31_000;

interface LoginResponse {
  access_token: string;
  username: string;
}

export default function Home() {
  const [filters, setFilters] = useState<FilterOptions>({
    property_types: [],
    bhks: [],
    locations: [],
    statuses: [],
  });
  const [loadingFilters, setLoadingFilters] = useState(true);
  const [loadingSearch, setLoadingSearch] = useState(false);
  const [matches, setMatches] = useState<PropertyMatch[]>([]);
  const [searchPerformed, setSearchPerformed] = useState(false);
  const [lastCriteria, setLastCriteria] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [username, setUsername] = useState<string | null>(null);
  const [checkingSession, setCheckingSession] = useState(true);

  const signOut = () => {
    sessionStorage.removeItem('property-matching-session');
    setAccessToken(null);
    setUsername(null);
    setMatches([]);
    setSearchPerformed(false);
  };

  const authorizedFetch = async (path: string, options: RequestInit = {}) => {
    const token = accessToken || sessionStorage.getItem('property-matching-session');
    const response = await fetch(`${API_BASE_URL}${path}`, {
      ...options,
      headers: {
        ...options.headers,
        Authorization: `Bearer ${token}`,
      },
    });
    if (response.status === 401) {
      signOut();
      throw new Error('Your session has expired. Please sign in again.');
    }
    return response;
  };

  // Fetch filter options on load
  useEffect(() => {
    const token = sessionStorage.getItem('property-matching-session');
    if (!token) {
      setCheckingSession(false);
      return;
    }
    fetch(`${API_BASE_URL}/auth/me`, { headers: { Authorization: `Bearer ${token}` } })
      .then(async (response) => {
        if (!response.ok) throw new Error();
        const user = await response.json();
        setAccessToken(token);
        setUsername(user.username);
      })
      .catch(() => sessionStorage.removeItem('property-matching-session'))
      .finally(() => setCheckingSession(false));
  }, []);

  useEffect(() => {
    if (accessToken) fetchFilters();
  }, [accessToken]);

  const fetchFilters = async (showLoading = true) => {
    try {
      if (showLoading) setLoadingFilters(true);
      setError(null);
      const res = await authorizedFetch('/filters');
      if (!res.ok) {
        throw new Error('Failed to retrieve filter options from backend.');
      }
      const data = await res.json();
      setFilters(data);
    } catch (err: any) {
      setError(err.message || 'Error occurred connecting to the backend server.');
    } finally {
      if (showLoading) setLoadingFilters(false);
    }
  };

  const handleSearch = async (params: {
    property_type: string;
    bhk: number | null;
    budget_cr: number | null;
    location: string;
    status: string;
    mode: 'STRICT' | 'FLEXIBLE';
  }) => {
    try {
      setLoadingSearch(true);
      setError(null);
      
      const response = await authorizedFetch('/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(params),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to retrieve search results.');
      }

      const data = await response.json();
      setMatches(data.matches);
      setSearchPerformed(true);
      setLastCriteria(params);
    } catch (err: any) {
      setError(err.message || 'Server connection failed.');
    } finally {
      setLoadingSearch(false);
    }
  };

  useEffect(() => {
    if (!accessToken) return;

    const refreshLiveInventory = async () => {
      try {
        await fetchFilters(false);
        if (!lastCriteria) return;

        const response = await authorizedFetch('/search', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(lastCriteria),
        });
        if (!response.ok) return;

        const data = await response.json();
        setMatches(data.matches);
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : 'Unable to refresh live inventory.');
      }
    };

    const intervalId = window.setInterval(refreshLiveInventory, LIVE_INVENTORY_POLL_MS);
    return () => window.clearInterval(intervalId);
  }, [accessToken, lastCriteria]);

  const handleLogin = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    try {
      setError(null);
      const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: form.get('username'), password: form.get('password') }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Unable to sign in.');
      const login = data as LoginResponse;
      sessionStorage.setItem('property-matching-session', login.access_token);
      setAccessToken(login.access_token);
      setUsername(login.username);
    } catch (err: any) {
      setError(err.message || 'Unable to sign in.');
    }
  };

  const refreshInventory = async () => {
    try {
      setLoadingFilters(true);
      setError(null);
      const response = await authorizedFetch('/inventory/refresh', { method: 'POST' });
      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Unable to refresh inventory.');
      }
      await fetchFilters();
    } catch (err: any) {
      setError(err.message || 'Unable to refresh inventory.');
    } finally {
      setLoadingFilters(false);
    }
  };

  if (checkingSession) {
    return <main className="min-h-screen bg-slate-50" />;
  }

  if (!accessToken) {
    return (
      <main className="min-h-screen bg-slate-100 flex items-center justify-center px-4 py-10 text-slate-900">
        <form onSubmit={handleLogin} className="w-full max-w-md bg-white border border-slate-200 shadow-sm rounded-lg p-8 space-y-6">
          <div>
            <p className="text-sm font-semibold text-blue-700">PROPERTY MATCHING AGENT</p>
            <h1 className="mt-2 text-2xl font-bold">Sign in</h1>
            <p className="mt-2 text-sm text-slate-600">Use an account approved by your administrator.</p>
          </div>
          {error && <p className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p>}
          <div>
            <label htmlFor="username" className="block text-sm font-medium text-slate-700 mb-2">Email or username</label>
            <input id="username" name="username" required autoComplete="username" className="w-full rounded-md border border-slate-300 px-3 py-2.5 focus:outline-none focus:ring-2 focus:ring-blue-500" />
          </div>
          <div>
            <label htmlFor="password" className="block text-sm font-medium text-slate-700 mb-2">Password</label>
            <input id="password" name="password" type="password" required autoComplete="current-password" className="w-full rounded-md border border-slate-300 px-3 py-2.5 focus:outline-none focus:ring-2 focus:ring-blue-500" />
          </div>
          <button type="submit" className="w-full rounded-md bg-blue-600 px-4 py-2.5 font-semibold text-white hover:bg-blue-700">Sign in</button>
        </form>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-slate-50 text-slate-900 pb-16">
      {/* Header bar */}
      <header className="bg-white border-b border-slate-200 py-6 mb-8 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-black text-blue-600 tracking-tight">PROPERTY MATCHING AGENT</h1>
              <p className="text-sm text-slate-500 font-medium">Find properties matching your requirements from the live inventory</p>
            </div>
            <button 
              onClick={refreshInventory}
              className="text-xs bg-slate-100 hover:bg-slate-200 text-slate-600 px-3 py-1.5 rounded-lg border border-slate-200 font-semibold transition"
            >
              Refresh inventory
            </button>
            <button onClick={signOut} className="ml-3 text-xs text-slate-600 hover:text-slate-900 font-semibold">
              Sign out {username ? `(${username})` : ''}
            </button>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
        {/* Error message Alert */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-800 rounded-xl p-4 flex items-center space-x-3">
            <svg className="w-6 h-6 text-red-500 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <div className="text-sm font-semibold">{error}</div>
          </div>
        )}

        {/* Loading filters state */}
        {loadingFilters ? (
          <div className="bg-white rounded-xl shadow-lg border border-slate-100 p-8 text-center">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-blue-500 border-t-transparent mb-4"></div>
            <p className="text-slate-500 font-medium">Reading inventory to build configuration filters...</p>
          </div>
        ) : (
          <SearchFilters filters={filters} onSearch={handleSearch} loading={loadingSearch} />
        )}

        {/* Results Component */}
        <PropertyResults matches={matches} searchPerformed={searchPerformed} reqCriteria={lastCriteria} />
      </div>
    </main>
  );
}
