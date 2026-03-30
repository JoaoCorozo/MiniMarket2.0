#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Minimarket Pily — Servidor Local v1.0
Ejecuta un servidor HTTP mínimo en localhost:7734
Guarda y carga los datos en datos.json dentro de esta carpeta.
"""

import http.server
import json
import os
import sys
import webbrowser
import threading
import time
from pathlib import Path
import subprocess
import logging
import traceback

# ── Configuración ──
PUERTO    = 7734
HOST      = '127.0.0.1'
URL_BASE  = f'http://{HOST}:{PUERTO}'

# Detectar si estamos empaquetados como .exe con PyInstaller
if getattr(sys, 'frozen', False):
    # El archivo html estará en la carpeta temporal de PyInstaller
    BUNDLE_DIR = Path(sys._MEIPASS)
    # Los datos de usuario se guardarán en la carpeta donde está el .exe real
    EXE_DIR = Path(sys.executable).parent
else:
    BUNDLE_DIR = Path(__file__).parent.resolve()
    EXE_DIR = BUNDLE_DIR

DATOS_JSON = EXE_DIR / 'datos.json'
HTML_FILE  = BUNDLE_DIR / 'Minimarket_Pily.html'
LOG_FILE   = EXE_DIR / 'minimarket.log'

# ── Configurar Logging ──
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Redirigir prints normales al log para que no se pierdan al correr sin consola
class StreamToLogger(object):
    def __init__(self, logger, level):
        self.logger = logger
        self.level = level
        self.linebuf = ''
    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.level, line.rstrip())
    def flush(self):
        pass

sys.stdout = StreamToLogger(logging.getLogger('STDOUT'), logging.INFO)
sys.stderr = StreamToLogger(logging.getLogger('STDERR'), logging.ERROR)

# ── Datos por defecto (primera vez) ──
DATOS_DEFAULT = {
    "categorias": [
        {"id":1,"nombre":"Bebidas",        "emoji":"🥤"},
        {"id":2,"nombre":"Lacteos",         "emoji":"🥛"},
        {"id":3,"nombre":"Panaderia",       "emoji":"🍞"},
        {"id":4,"nombre":"Almacen / Secos", "emoji":"🫙"},
        {"id":5,"nombre":"Limpieza",        "emoji":"🧴"},
        {"id":6,"nombre":"Golosinas",       "emoji":"🍫"},
        {"id":7,"nombre":"Cigarrillos",     "emoji":"🚬"}
    ],
    "productos":  [],
    "ventas":     [],
    "nextCatId":   8,
    "nextProdId":  1,
    "nextVentaId": 1
}

# ── Cargar / guardar datos ──
def cargar_datos():
    if DATOS_JSON.exists():
        try:
            with open(DATOS_JSON, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[ERROR] datos.json corrupto, usando defaults: {e}")
    return json.loads(json.dumps(DATOS_DEFAULT))  # deep copy

def guardar_datos(datos):
    try:
        with open(DATOS_JSON, 'w', encoding='utf-8') as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"[ERROR] No se pudo guardar datos.json: {e}")
        return False

# ── Handler HTTP ──
class PilyHandler(http.server.BaseHTTPRequestHandler):

    def log_message(self, fmt, *args):
        # Solo logear errores, no cada request
        if '404' in str(args) or '500' in str(args):
            print(f"[{args}]")

    def send_json(self, code, data):
        body = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(body)

    def send_html(self):
        try:
            with open(HTML_FILE, 'r', encoding='utf-8') as f:
                body = f.read().encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except Exception as e:
            self.send_error(500, str(e))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        if self.path in ('/', '/index.html', '/Minimarket_Pily.html'):
            self.send_html()

        elif self.path == '/api/datos':
            datos = cargar_datos()
            self.send_json(200, datos)

        elif self.path == '/api/ping':
            self.send_json(200, {'ok': True, 'version': '1.0'})

        else:
            self.send_error(404, 'No encontrado')

    def do_POST(self):
        if self.path == '/api/datos':
            length = int(self.headers.get('Content-Length', 0))
            body   = self.rfile.read(length)
            try:
                datos = json.loads(body.decode('utf-8'))
                ok    = guardar_datos(datos)
                self.send_json(200 if ok else 500, {'ok': ok})
            except Exception as e:
                self.send_json(400, {'ok': False, 'error': str(e)})

        elif self.path == '/api/reset':
            ok = guardar_datos(json.loads(json.dumps(DATOS_DEFAULT)))
            self.send_json(200, {'ok': ok})

        else:
            self.send_error(404, 'No encontrado')


# ── Main ──
def main():
    print("=" * 50)
    print("  🍄 MINIMARKET PILY — Sistema POS v1.0 (Portable)")
    print("=" * 50)
    print(f"\n  Ejecutable Dir: {EXE_DIR}")
    print(f"  HTML Dir:       {BUNDLE_DIR}")
    print(f"  Datos:          {DATOS_JSON.name}")
    print(f"  Servidor local: {URL_BASE}")

    if not HTML_FILE.exists():
        print(f"\n[ERROR] No se encontró Minimarket_Pily.html")
        print(f"  Esperado en: {HTML_FILE}")
        input("\nPresioná Enter para salir...")
        sys.exit(1)

    # Crear datos.json si no existe
    if not DATOS_JSON.exists():
        guardar_datos(json.loads(json.dumps(DATOS_DEFAULT)))
        print("\n  ✓ datos.json creado (primera vez)")
    else:
        datos = cargar_datos()
        n_ventas = len(datos.get('ventas', []))
        n_prods  = len([p for p in datos.get('productos', []) if p.get('activo')])
        print(f"\n  ✓ datos.json cargado")
        print(f"    · {n_prods} productos activos")
        print(f"    · {n_ventas} ventas registradas")

    print(f"\n  Iniciando aplicación en ventana nativa...")

    # Función para ejecutar el servidor en un hilo
    def run_server():
        try:
            servidor = http.server.HTTPServer((HOST, PUERTO), PilyHandler)
            servidor.serve_forever()
        except OSError as e:
            if 'Address already in use' in str(e):
                print(f"\n[AVISO] El puerto {PUERTO} ya está en uso. Conectando al existente...")
            else:
                print(f"Error interno del servidor: {e}")

    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    # Dar un instante para que el servidor levante
    time.sleep(0.5)

    try:
        # Intenta abrir Microsoft Edge en modo aplicación (ventana nativa sin UI de navegador)
        edge_paths = [
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
        ]
        edge_exe = next((p for p in edge_paths if os.path.exists(p)), None)
        
        if edge_exe:
            subprocess.Popen([edge_exe, f'--app={URL_BASE}'])
        else:
            # Fallback a navegador por defecto
            webbrowser.open(URL_BASE)
            
        print("\n  [Dejá esta ventana negra abierta mientras usás el sistema]")
        print("  [Cerrala cuando termines para apagar el servidor]\n")
        
        # Mantener el hilo principal vivo
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n  Sistema cerrado. ¡Hasta luego!")
    except Exception as e:
        print(f"Error al abrir la ventana: {e}")
        input("Presione Enter para salir...")


if __name__ == '__main__':
    main()
