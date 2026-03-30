import os
import shutil
import datetime
import sys
import time

def hacer_respaldo():
    # Detectar el directorio donde está este ejecutable
    if getattr(sys, 'frozen', False):
        exe_dir = os.path.dirname(sys.executable)
    else:
        exe_dir = os.path.dirname(os.path.abspath(__file__))

    archivo_origen = os.path.join(exe_dir, 'datos.json')
    carpeta_destino = r'C:\Respaldos_Minimarket'

    print("=======================================")
    print("  RESPALDO DE BASE DE DATOS MINIMARKET ")
    print("=======================================\n")

    if not os.path.exists(archivo_origen):
        print(f"[ERROR] No se encontro ninguna base de datos en:\n{archivo_origen}")
        print("\nEl programa de respaldo debe estar en la misma carpeta que datos.json")
        time.sleep(5)
        return

    try:
        if not os.path.exists(carpeta_destino):
            os.makedirs(carpeta_destino)
            print(f"[INFO] Se ha creado la carpeta destino: {carpeta_destino}")

        fecha_hora = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        nombre_respaldo = f"datos_respaldo_{fecha_hora}.json"
        ruta_destino = os.path.join(carpeta_destino, nombre_respaldo)

        shutil.copy2(archivo_origen, ruta_destino)
        print(f"[EXITO] La base de datos se ha respaldado correctamente.")
        print(f"[INFO] Ruta: {ruta_destino}")
        
    except Exception as e:
        print(f"[ERROR] Ocurrio un problema al copiar el archivo: {e}")

    print("\nCerrando en 5 segundos...")
    time.sleep(5)

if __name__ == '__main__':
    hacer_respaldo()
