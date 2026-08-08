#!/usr/bin/env python3
"""
Mock server for frontend testing
"""

import json
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse

class MockHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'<h1>Mock Backend Running</h1><p>Frontend can connect to this server</p>')
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        if self.path == '/execute-full-scale':
            self.handle_full_scale_request()
        else:
            self.send_response(404)
            self.end_headers()
    
    def handle_full_scale_request(self):
        """Return mock full-scale analysis data"""
        try:
            # Load mock data
            with open('mock_backend_response.json', 'r') as f:
                mock_data = json.load(f)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            
            self.wfile.write(json.dumps(mock_data).encode())
            print("✅ Mock data sent to frontend")
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"ok": False, "error": str(e)}).encode())
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

def run_mock_server(port=8000):
    server = HTTPServer(('127.0.0.1', port), MockHandler)
    print(f"🚀 Mock server running on http://127.0.0.1:{port}")
    print("📊 Serving mock full-scale data to frontend")
    server.serve_forever()

if __name__ == "__main__":
    run_mock_server()
