# Domain Name Checker

Generate and bulk-check short domain name availability across `.com` and `.io`.

## How it works

- `.com` availability is checked via [Verisign's public RDAP API](https://rdap.verisign.com) directly from the browser
- `.io` availability is checked via a local Python server that queries the `whois.nic.io` WHOIS server (required to avoid CORS restrictions)

## Requirements

- Python 3.6+
- A modern browser (Chrome, Firefox, Safari, Edge)

## Setup

1. Clone the repo:
   ```bash
   git clone <repo-url>
   cd domain_name_generator_two
   ```

2. Start the local server:
   ```bash
   python3 server.py
   ```

   If port 8080 is already taken, pass another one: `python3 server.py 8087`.

3. Open [http://localhost:8080](http://localhost:8080) in your browser.

> Don't open `index.html` directly from disk. Browsers treat `file://` pages as a unique origin and block their cross-origin requests outright, so the `.com` RDAP lookups fail with an error like *"'file:' URLs are treated as unique security origins"*. Serve the page over HTTP with `server.py`.

## Usage

| Setting | Description |
|---|---|
| **Name Length** | Maximum character count of the domain name (2–15) |
| **Strategy** | `All Combinations` — every possible string; `CV Patterns` — strict consonant/vowel alternation; `Pronounceable` — no more than 2 consecutive vowels or consonants |
| **Requests/Second** | How fast to check domains. Stay under ~15 to avoid rate-limiting |
| **Prefix** | Lock the start of the name (e.g. `ba` or `be, bi` for multiple) |
| **Suffix** | Lock the end of the name (e.g. `fi` or `ly, er` for multiple) |
| **TLDs** | Check `.com`, `.io`, or both |

Click **Start** to begin. Results show only names with at least one available TLD. Use **Export CSV** to download the results.

## Rate limiting notes

- The Verisign RDAP endpoint is public but unauthenticated — keep requests under ~15/s to avoid 429 errors
- The WHOIS server enforces a 300ms minimum gap between requests (handled automatically by the server)

## Files

| File | Purpose |
|---|---|
| `server.py` | Python HTTP server — serves `index.html` and proxies `.io` WHOIS lookups |
| `index.html` | Frontend — name generation and domain checking UI |
