
import json
import http.server
import socketserver
import webbrowser
import threading
import urllib.parse
from pathlib import Path
from http import HTTPStatus

SUCCESS_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Authentication Successful</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background-color: #000; color: #fff; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; }
        .container { text-align: center; animation: fadein 1s; }
        h1 { font-size: 24px; color: #10b981; margin-bottom: 16px; }
        p { font-size: 14px; color: #6b7280; }
        .logo { width: 48px; height: 48px; background: #fff; border-radius: 6px; margin: 0 auto 24px; }
        @keyframes fadein { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo"></div>
        <h1>Authentication Successful</h1>
        <p>You can close this window and return to your terminal.</p>
        <p style="font-size: 10px; margin-top: 32px; color: #333;">System Secure Auth v1.0</p>
    </div>
</body>
</html>
"""

class OAuthCallbackHandler(http.server.BaseHTTPRequestHandler):
    tokens = None
    
    def log_message(self, format, *args):
        pass  # Suppress logging

    def do_GET(self):
        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)
        
        access_token = params.get('access_token', [None])[0]
        refresh_token = params.get('refresh_token', [None])[0]
        verified_tier = params.get('tier', ["hobby"])[0]
        signature = params.get('sig', [None])[0]
        
        if access_token:
            self.server.tokens = {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "tier": verified_tier,
                "signature": signature
            }
            
            self.send_response(HTTPStatus.OK)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(SUCCESS_PAGE.encode('utf-8'))
        else:
            self.send_response(HTTPStatus.BAD_REQUEST)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b"Authentication Failed: No tokens received.")
        
        # Shutdown server in a separate thread to allow response to finish
        threading.Thread(target=self.server.shutdown).start()

def start_auth_server(port=54321):
    """
    Starts an ephemeral HTTP server to capture OAuth tokens.
    Returns: dict with tokens or None if failed/timed out.
    """
    server = socketserver.TCPServer(("localhost", port), OAuthCallbackHandler)
    server.tokens = None
    
    # Run the server until one request is handled or manually stopped
    # We use server.serve_forever() but trigger shutdown() inside the handler
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        
    return server.tokens
