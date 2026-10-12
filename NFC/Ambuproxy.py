
"""
Proxy local para el simulador de ambulancias.

Sirve el simulador en http://localhost:8000 y reenvia las peticiones
http://localhost:8000/traccar/... al servidor Traccar (solo GET), asi el
navegador no bloquea la lectura por CORS.

Uso (en la carpeta donde estan este archivo y el HTML del simulador):
    python proxy_traccar.py
    python proxy_traccar.py https://mi-servidor-traccar.com   (servidor propio)

Para detenerlo: Ctrl + C
"""
import http.server
import os
import sys
import urllib.error
import urllib.request

TARGET = (sys.argv[1] if len(sys.argv) > 1 else "https://demo.traccar.org").rstrip("/")
PORT = 8000
os.chdir(os.path.dirname(os.path.abspath(__file__)))


class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if not self.path.startswith("/traccar/"):
            return super().do_GET()
        url = TARGET + self.path[len("/traccar"):]
        headers = {"Accept": "application/json"}
        auth = self.headers.get("Authorization")
        if auth:
            headers["Authorization"] = auth
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=15) as r:
                body, code = r.read(), r.status
                ctype = r.headers.get("Content-Type", "application/json")
        except urllib.error.HTTPError as e:
            body, code, ctype = e.read(), e.code, "text/plain"
        except Exception as e:
            body, code, ctype = str(e).encode(), 502, "text/plain"
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    print("Servidor Traccar de destino:", TARGET)
    print("Abre: http://localhost:%d/simulador-ambulancias-neiva-traccar.html" % PORT)
    print("En el simulador, URL de Traccar: http://localhost:%d/traccar" % PORT)
    print("Ctrl + C para detener.")
    http.server.ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()