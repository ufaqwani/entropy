const BASE = process.env.REACT_APP_API_BASE_URL || ''; // '' means same-origin (Netlify)


if (!BASE) {
  // Warn during local builds if the var is missing
  // eslint-disable-next-line no-console
  console.warn('REACT_APP_API_BASE_URL is not set');
}

export async function api(path, { method = 'GET', body, headers = {}, credentials = 'include' } = {}) {
  const res = await fetch(`${BASE}${path}`, {
    method,
    headers: { 'Content-Type': 'application/json', ...headers },
    credentials,
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) {
    const text = await res.text().catch(() => '');
    throw new Error(`${res.status} ${res.statusText} ${text}`.trim());
  }
  const ct = res.headers.get('content-type') || '';
  return ct.includes('application/json') ? res.json() : null;
}
