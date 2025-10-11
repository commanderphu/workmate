// Erzwingt HTTPS für versehentlich harte HTTP-Calls im Dev
if (import.meta.env.DEV) {
  const origFetch = window.fetch;
  window.fetch = (input: RequestInfo | URL, init?: RequestInit) => {
    if (typeof input === 'string' && input.startsWith('http://api.workmate.test')) {
      input = input.replace(/^http:\/\//, 'https://');
      console.warn('[https-guard] upgraded to', input);
    }
    return origFetch(input as any, init);
  };
}
