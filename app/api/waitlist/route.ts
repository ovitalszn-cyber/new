import { NextResponse } from 'next/server';

interface BrevoResponse {
  message?: string;
  code?: string;
}

export async function POST(request: Request) {
  try {
    const { email } = await request.json();

    if (typeof email !== 'string' || !email.includes('@')) {
      return NextResponse.json({ error: 'Please provide a valid email address.' }, { status: 400 });
    }

    const apiKey = process.env.BREVO_API_KEY;
    const listId = process.env.BREVO_LIST_ID;

    if (!apiKey || !listId) {
      console.error('Missing Brevo configuration.');
      return NextResponse.json(
        { error: 'Waitlist configuration is incomplete. Please contact support.' },
        { status: 500 },
      );
    }

    const brevoResponse = await fetch('https://api.brevo.com/v3/contacts', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'api-key': apiKey,
      },
      body: JSON.stringify({
        email,
        listIds: [Number(listId)],
        updateEnabled: true,
      }),
    });

    const data = (await brevoResponse.json().catch(() => ({}))) as BrevoResponse;

    if (!brevoResponse.ok) {
      const message = data?.message || 'Failed to subscribe email.';
      return NextResponse.json({ error: message }, { status: brevoResponse.status });
    }

    return NextResponse.json({ success: true });
  } catch (error) {
    console.error('Brevo waitlist error', error);
    return NextResponse.json({ error: 'Unexpected server error. Please try again later.' }, { status: 500 });
  }
}
