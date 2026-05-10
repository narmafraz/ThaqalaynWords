#!/usr/bin/env python3
# encoding: utf-8
"""Local dev server for ThaqalaynWords with CORS enabled.

Mirrors ThaqalaynData's `serve.py` — same pattern, different port. The
Angular UI in development fetches word JSON from this server.

Usage:
    python serve.py
"""
from http.server import HTTPServer, SimpleHTTPRequestHandler
from socketserver import ThreadingMixIn


class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in separate threads for concurrent access."""
    daemon_threads = True


class CORSRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        return super(CORSRequestHandler, self).end_headers()

    def log_message(self, format, *args):
        """Suppress verbose request logging."""
        pass


httpd = ThreadingHTTPServer(('localhost', 8889), CORSRequestHandler)
print('Serving on http://localhost:8889/ (threaded)')
httpd.serve_forever()
