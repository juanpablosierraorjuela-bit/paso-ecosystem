import os

# Este script elimina el conflicto en views.py
# Comenta la línea que intenta sobrescribir la propiedad inteligente is_open_now

def arreglar_conflicto_vista():
    ruta = "apps/businesses/views.py"
    print(f"🔧 Reparando conflicto en: {ruta}")
    
    if not os.path.exists(ruta):
        print("❌ No encontré el archivo views.py")
        return

    with open(ruta, "r", encoding="utf-8") as f:
        lineas = f.readlines()

    lineas_nuevas = []
    corregido = False
    
    for linea in lineas:
        # Buscamos donde intenta ASIGNAR valor (=) a la propiedad
        if ".is_open_now =" in linea:
            # Comentamos la línea para desactivarla
            lineas_nuevas.append(f"            # {linea.strip()}  # FIX: Conflict with model property\n")
            corregido = True
        else:
            lineas_nuevas.append(linea)

    if corregido:
        with open(ruta, "w", encoding="utf-8") as f:
            f.writelines(lineas_nuevas)
        print("✅ views.py corregido: Se eliminó la asignación manual conflictiva.")
    else:
        print("ℹ️ No encontré la línea conflictiva (¿ya estaba arreglado?).")

if __name__ == "__main__":
    arreglar_conflicto_vista()