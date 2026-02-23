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

# ── Configuración ──
PUERTO    = 7734
HOST      = '127.0.0.1'
URL_BASE  = f'http://{HOST}:{PUERTO}'

# Directorio donde está este script (portable)
BASE_DIR  = Path(__file__).parent.resolve()
DATOS_JSON = BASE_DIR / 'datos.json'
HTML_FILE  = BASE_DIR / 'Minimarket_Pily.html'

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
    "productos": [
        {"id":1, "codigo":"001","nombre":"Coca-Cola 500ml",  "catId":1,"precio":1200,"stock":24,"stockMin":5, "activo":True,"granel":False},
        {"id":2, "codigo":"002","nombre":"Agua mineral 1.5L","catId":1,"precio":800, "stock":15,"stockMin":10,"activo":True,"granel":False},
        {"id":3, "codigo":"003","nombre":"Pan marraqueta",   "catId":3,"precio":0,   "stock":0, "stockMin":0, "activo":True,"granel":True},
        {"id":4, "codigo":"004","nombre":"Leche entera 1L",  "catId":2,"precio":1100,"stock":3, "stockMin":5, "activo":True,"granel":False},
        {"id":5, "codigo":"005","nombre":"Fideos spaghetti", "catId":4,"precio":900, "stock":20,"stockMin":5, "activo":True,"granel":False},
        {"id":6, "codigo":"006","nombre":"Aceite 900ml",     "catId":4,"precio":2200,"stock":7, "stockMin":4, "activo":True,"granel":False},
        {"id":7, "codigo":"007","nombre":"Arroz 1kg",        "catId":4,"precio":1300,"stock":12,"stockMin":6, "activo":True,"granel":False},
        {"id":8, "codigo":"008","nombre":"Yogur frutado",    "catId":2,"precio":600, "stock":2, "stockMin":5, "activo":True,"granel":False},
        {"id":9, "codigo":"009","nombre":"Marlboro Rojo",    "catId":7,"precio":3200,"stock":30,"stockMin":5, "activo":True,"granel":False},
        {"id":10,"codigo":"010","nombre":"Belmont Box",      "catId":7,"precio":2800,"stock":20,"stockMin":5, "activo":True,"granel":False},
        {"id":11,"codigo":"011","nombre":"Pan a granel",     "catId":3,"precio":0,   "stock":0, "stockMin":0, "activo":True,"granel":True}
    ],
    "ventas":      [],
    "nextCatId":   8,
    "nextProdId":  12,
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


# ── Abrir navegador después de un momento ──
def abrir_navegador():
    time.sleep(1.2)
    webbrowser.open(URL_BASE)


# ── Main ──
def main():
    print("=" * 50)
    print("  🍄 MINIMARKET PILY — Sistema POS v1.0")
    print("=" * 50)
    print(f"\n  Directorio: {BASE_DIR}")
    print(f"  Datos:      {DATOS_JSON.name}")
    print(f"  Servidor:   {URL_BASE}")

    if not HTML_FILE.exists():
        print(f"\n[ERROR] No se encontró Minimarket_Pily.html")
        print(f"  Asegurate de que esté en: {BASE_DIR}")
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

    print(f"\n  Abriendo navegador en {URL_BASE} ...")
    print("\n  [Dejá esta ventana abierta mientras usás el sistema]")
    print("  [Cerrala cuando termines o presioná Ctrl+C]\n")

    threading.Thread(target=abrir_navegador, daemon=True).start()

    try:
        servidor = http.server.HTTPServer((HOST, PUERTO), PilyHandler)
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\n\n  Sistema cerrado. ¡Hasta luego!")
    except OSError as e:
        if 'Address already in use' in str(e):
            print(f"\n[AVISO] El puerto {PUERTO} ya está en uso.")
            print(f"  Quizás el sistema ya está corriendo.")
            print(f"  Abrí tu navegador en: {URL_BASE}")
            webbrowser.open(URL_BASE)
            input("\nPresioná Enter para salir...")
        else:
            raise


if __name__ == '__main__':
    main()
