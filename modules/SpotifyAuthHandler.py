from http.server import BaseHTTPRequestHandler
import urllib.parse


class SpotifyAuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/callback"):
            params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            self.server.authorization_code = params['code'][0]
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'Authorization code received. You can close this window.')
        else:
            self.send_response(404)
            self.end_headers()
