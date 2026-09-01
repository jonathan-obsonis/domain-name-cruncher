import errno
import http.server
import json
import os
import socket
import sys
import urllib.parse
import threading
import time

whois_lock = threading.Lock()
last_whois_time = 0
WHOIS_INTERVAL = 0.3

class Handler(http.server.ThreadingHTTPServer if hasattr(http.server, 'ThreadingHTTPServer') else http.server.HTTPServer):
    pass

class RequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == '/check-io':
            params = urllib.parse.parse_qs(parsed.query)
            domain = params.get('domain', [''])[0]
            if not domain or not domain.replace('-', '').isalnum():
                self.send_json(400, {'error': 'invalid domain'})
                return
            try:
                result = whois_serial(f'{domain}.io')
                available = 'Domain not found' in result
                self.send_json(200, {
                    'domain': f'{domain}.io',
                    'status': 'available' if available else 'taken',
                })
            except Exception as e:
                self.send_json(500, {'error': str(e)})
            return
        super().do_GET()

    def send_json(self, code, data):
        body = json.dumps(data).encode()
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', len(body))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        pass

def whois_serial(domain):
    global last_whois_time
    with whois_lock:
        now = time.monotonic()
        wait = WHOIS_INTERVAL - (now - last_whois_time)
        if wait > 0:
            time.sleep(wait)

        for attempt in range(3):
            try:
                result = whois_lookup(domain)
                last_whois_time = time.monotonic()
                return result
            except Exception:
                if attempt == 2:
                    raise
                time.sleep(1 * (attempt + 1))

def whois_lookup(domain):
    with socket.create_connection(('whois.nic.io', 43), timeout=10) as sock:
        sock.sendall((domain + '\r\n').encode())
        response = b''
        while True:
            chunk = sock.recv(4096)
            if not chunk:
                break
            response += chunk
    return response.decode('utf-8', errors='replace')

if __name__ == '__main__':
    port = int(sys.argv[1] if len(sys.argv) > 1 else os.environ.get('PORT', 8080))
    try:
        server = http.server.ThreadingHTTPServer(('', port), RequestHandler)
    except OSError as e:
        if e.errno == errno.EADDRINUSE:
            print(f'Port {port} is already in use. Try: python3 server.py {port + 1}')
            raise SystemExit(1)
        raise
    print(f'Server running on http://localhost:{port}')
    server.serve_forever()
