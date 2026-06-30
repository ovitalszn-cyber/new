import { NextResponse } from 'next/server';

const BACKEND_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'https://backend.kashrock.com';

export async function POST(request: Request) {
  try {
    const { email } = await request.json();

    if (typeof email !== 'string' || !email.includes('@')) {
      return NextResponse.json({ error: 'Please provide a valid email address.' }, { status: 400 });
    }

    const backendResponse = await fetch(`${BACKEND_URL}/v1/dev/waitlist`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: email.trim(), source: 'maintenance' }),
    });

    const data = (await backendResponse.json().catch(() => ({}))) as { detail?: string; error?: string };

    if (!backendResponse.ok) {
      const message = data.detail || data.error || 'Failed to save email.';
      return NextResponse.json({ error: message }, { status: backendResponse.status });
    }

    return NextResponse.json({ success: true });
  } catch (error) {
    console.error('Waitlist signup error', error);
    return NextResponse.json({ error: 'Unexpected server error. Please try again later.' }, { status: 500 });
  }
}
