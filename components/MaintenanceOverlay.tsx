'use client';

import { FormEvent, useState } from 'react';

import { MAINTENANCE_MESSAGE } from '@/lib/maintenance';

export default function MaintenanceOverlay() {
  const [email, setEmail] = useState('');
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');
  const [errorMessage, setErrorMessage] = useState('');

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const trimmed = email.trim();
    if (!trimmed.includes('@')) {
      setStatus('error');
      setErrorMessage('Please enter a valid email address.');
      return;
    }

    setStatus('loading');
    setErrorMessage('');

    try {
      const response = await fetch('/api/waitlist', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: trimmed }),
      });

      const data = (await response.json().catch(() => ({}))) as { error?: string };

      if (!response.ok) {
        setStatus('error');
        setErrorMessage(data.error || 'Something went wrong. Please try again.');
        return;
      }

      setStatus('success');
      setEmail('');
    } catch {
      setStatus('error');
      setErrorMessage('Something went wrong. Please try again.');
    }
  }

  return (
    <div
      className="flex min-h-screen items-center justify-center bg-[#08090A] px-6"
      role="main"
      aria-labelledby="maintenance-title"
    >
      <div className="w-full max-w-lg rounded-sm border border-white/10 bg-[#0f1012] p-10 text-center shadow-2xl">
        <img
          src="/kashrock-logo.svg"
          alt="KashRock"
          className="mx-auto mb-8 h-10 w-auto"
        />

        <p className="mb-3 text-xs font-medium uppercase tracking-[0.2em] text-zinc-500">
          New edition
        </p>

        <h1
          id="maintenance-title"
          className="mb-4 text-2xl font-semibold tracking-tight text-white"
        >
          Expanding the catalog
        </h1>

        <p className="mb-8 text-sm leading-relaxed text-zinc-400">
          {MAINTENANCE_MESSAGE}
        </p>

        {status === 'success' ? (
          <p className="rounded-sm border border-emerald-500/20 bg-emerald-500/10 px-4 py-3 text-sm text-emerald-300">
            You&apos;re on the list. We&apos;ll email you when we&apos;re back.
          </p>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-3 text-left">
            <label htmlFor="maintenance-email" className="sr-only">
              Email address
            </label>
            <input
              id="maintenance-email"
              type="email"
              name="email"
              autoComplete="email"
              required
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              placeholder="you@company.com"
              disabled={status === 'loading'}
              className="w-full rounded-sm border border-white/10 bg-[#08090A] px-4 py-2.5 text-sm text-white placeholder:text-zinc-600 outline-none transition-colors focus:border-white/25 disabled:opacity-60"
            />
            <button
              type="submit"
              disabled={status === 'loading'}
              className="w-full rounded-sm bg-white px-5 py-2.5 text-sm font-medium text-black transition-colors hover:bg-zinc-200 disabled:cursor-not-allowed disabled:opacity-70"
            >
              {status === 'loading' ? 'Submitting...' : 'Notify me when we\'re back'}
            </button>
            {status === 'error' && errorMessage ? (
              <p className="text-center text-sm text-red-400">{errorMessage}</p>
            ) : null}
          </form>
        )}
      </div>
    </div>
  );
}
