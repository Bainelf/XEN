from http.server import BaseHTTPRequestHandler, HTTPServer

class Sniffer(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        print("\n📦 COLIS REÇU !")
        print(f"Taille : {len(post_data)} octets")
        print("Contenu brut (extrait) :", post_data[:200])
        self.send_response(200)
        self.end_headers()

print("👂 Sniffer actif sur le port 27001... (Fais un endmatch !)")
HTTPServer(('127.0.0.1', 27001), Sniffer).serve_forever()

