import { randomBytes } from 'node:crypto'

function escapeHtml(value: string) {
  return value
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;')
}

export function createKeyDeliveryHtml(apiKey: string, returnTo: string) {
  const nonce = randomBytes(18).toString('base64url')
  const safeKey = escapeHtml(apiKey)
  const safeReturnTo = escapeHtml(returnTo)
  const scriptKey = JSON.stringify(apiKey).replaceAll('<', '\\u003c')
  return {
    nonce,
    html: `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Your KashRock API key</title>
  <style>
    body{margin:0;background:#08090a;color:#e3e5e7;font:16px system-ui;display:grid;min-height:100vh;place-items:center}
    main{width:min(680px,calc(100% - 48px));background:#0c0d0f;border:1px solid #ffffff1a;padding:32px;border-radius:8px}
    h1{font-size:24px}p{color:#a1a1aa;line-height:1.5}code{display:block;background:#000;padding:16px;overflow-wrap:anywhere;color:#86efac}
    .actions{display:flex;gap:12px;margin-top:20px}button,a{border:0;border-radius:4px;padding:11px 16px;font-weight:600}
    button{background:#fff;color:#000;cursor:pointer}a{border:1px solid #ffffff2a;color:#fff;text-decoration:none}
  </style>
</head>
<body>
  <main>
    <h1>Your API key is ready</h1>
    <p>Copy it now and store it securely. It will not be shown again.</p>
    <code id="key">${safeKey}</code>
    <div class="actions">
      <button id="copy" type="button">Copy key</button>
      <a href="${safeReturnTo}">Continue</a>
    </div>
  </main>
  <script nonce="${nonce}">
    history.replaceState({}, '', '/auth/complete');
    const key = ${scriptKey};
    document.getElementById('copy').addEventListener('click', async (event) => {
      await navigator.clipboard.writeText(key);
      event.currentTarget.textContent = 'Copied';
    });
  </script>
</body>
</html>`,
  }
}
