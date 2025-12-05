import { NextResponse } from 'next/server';
import crypto from 'crypto';

const API_KEY = process.env.MAILCHIMP_API_KEY;
const AUDIENCE_ID = process.env.MAILCHIMP_AUDIENCE_ID;
const SERVER_PREFIX = process.env.MAILCHIMP_SERVER_PREFIX;

export async function POST(req: Request) {
  if (!API_KEY || !AUDIENCE_ID || !SERVER_PREFIX) {
    return NextResponse.json(
      { success: false, error: 'Server not configured for Mailchimp.' },
      { status: 500 }
    );
  }

  try {
    const { email } = await req.json();

    if (!email || typeof email !== 'string' || !email.includes('@')) {
      return NextResponse.json(
        { success: false, error: 'Please provide a valid email address.' },
        { status: 400 }
      );
    }

    const subscriberHash = crypto
      .createHash('md5')
      .update(email.toLowerCase())
      .digest('hex');

    const url = `https://${SERVER_PREFIX}.api.mailchimp.com/3.0/lists/${AUDIENCE_ID}/members/${subscriberHash}`;
    const auth = Buffer.from(`anystring:${API_KEY}`).toString('base64');

    const mcResponse = await fetch(url, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Basic ${auth}`,
      },
      body: JSON.stringify({
        email_address: email,
        status_if_new: 'subscribed',
      }),
    });

    if (!mcResponse.ok) {
      let errorMessage = 'Failed to subscribe. Please try again.';

      try {
        const errorData = await mcResponse.json();
        if (errorData?.detail) {
          errorMessage = errorData.detail;
        }
      } catch {
        // ignore JSON parse errors
      }

      return NextResponse.json(
        { success: false, error: errorMessage },
        { status: mcResponse.status }
      );
    }

    return NextResponse.json({
      success: true,
      message: "You're on the list! We'll be in touch soon.",
    });
  } catch (error) {
    console.error('Mailchimp subscribe error', error);
    return NextResponse.json(
      { success: false, error: 'Something went wrong. Please try again.' },
      { status: 500 }
    );
  }
}
