import { NextResponse } from 'next/server';
import nodemailer from 'nodemailer';

const SMTP_HOST = process.env.NEO_SMTP_HOST || 'smtp0001.neo.space';
const SMTP_PORT = parseInt(process.env.NEO_SMTP_PORT || '465', 10);
const SMTP_USER = process.env.NEO_SMTP_USER;
const SMTP_PASS = process.env.NEO_SMTP_PASS;
const RECIPIENT = process.env.NEO_SMTP_RECIPIENT || 'support@kashrock.com';

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { fullName, email, message } = body as {
      fullName?: string;
      email?: string;
      message?: string;
    };

    if (!fullName || !email || !message) {
      return NextResponse.json({ error: 'Name, email, and message are required.' }, { status: 400 });
    }
    if (!email.includes('@')) {
      return NextResponse.json({ error: 'Please provide a valid email address.' }, { status: 400 });
    }

    const transporter = nodemailer.createTransport({
      host: SMTP_HOST,
      port: SMTP_PORT,
      secure: SMTP_PORT === 465,
      auth: { user: SMTP_USER, pass: SMTP_PASS },
    });

    const mailOptions = {
      from: `"${fullName}" <${email}>`,
      to: RECIPIENT,
      subject: `Contact form: ${fullName}`,
      text: [
        `New contact form submission`,
        ``,
        `Full Name: ${fullName}`,
        `Email: ${email}`,
        ``,
        `Message:`,
        message,
      ].join('\n'),
      html: [
        `<h2>New Contact Form Submission</h2>`,
        `<table style="border-collapse:collapse; font-family:sans-serif;">`,
        `<tr><td style="padding:4px 12px 4px 0; font-weight:bold;">Full Name</td><td style="padding:4px 0;">${escapeHtml(fullName)}</td></tr>`,
        `<tr><td style="padding:4px 12px 4px 0; font-weight:bold;">Email</td><td style="padding:4px 0;">${escapeHtml(email)}</td></tr>`,
        `</table>`,
        `<h3 style="margin-top:16px;">Message</h3>`,
        `<p style="white-space:pre-wrap;">${escapeHtml(message)}</p>`,
      ].join(''),
    };

    await transporter.sendMail(mailOptions);
    return NextResponse.json({ success: true });
  } catch (error) {
    console.error('Contact form error', error);
    return NextResponse.json({ error: 'Failed to send message. Please try again later.' }, { status: 500 });
  }
}

function escapeHtml(str: string): string {
  return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}
