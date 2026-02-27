#!/usr/bin/env python3
import http.server
import ssl

# ---------------- CONFIG ----------------
PORT_HTTPS = 4443        # HTTPS port
PORT_HTTP  = 8080        # HTTP fallback port
ADDRESS    = '0.0.0.0'   # Listen on all interfaces
CERT_FILE  = 'cert.pem'
KEY_FILE   = 'key.pem'
# ----------------------------------------

class UTF8Handler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Force UTF-8 for text files
        if self.path.endswith(".txt"):
            self.send_header("Content-Type", "text/plain; charset=UTF-8")
        super().end_headers()

handler = UTF8Handler


def start_https():
    try:
        httpd = http.server.HTTPServer((ADDRESS, PORT_HTTPS), handler)

        # Legacy TLS 1.0 for old Safari (iOS 4.x)
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        # Allow weak ciphers so ancient clients can connect (insecure – local LAN only!)
        context.set_ciphers('ALL:@SECLEVEL=0')

        context.load_cert_chain(certfile=CERT_FILE, keyfile=KEY_FILE)
        httpd.socket = context.wrap_socket(httpd.socket, server_side=True)

        print(f"🔐  HTTPS server running at https://{ADDRESS}:{PORT_HTTPS}  (TLS 1.0, weak ciphers enabled)")
        httpd.serve_forever()

    except Exception as e:
        print(f"[!] HTTPS failed: {e}")
        start_http()


def start_http():
    httpd = http.server.HTTPServer((ADDRESS, PORT_HTTP), handler)
    print(f"⚠️  Falling back to HTTP at http://{ADDRESS}:{PORT_HTTP}")
    httpd.serve_forever()


if __name__ == '__main__':
    start_https()
