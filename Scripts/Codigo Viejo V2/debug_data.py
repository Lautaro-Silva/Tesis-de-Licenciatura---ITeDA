import pandas as pd
import numpy as np
import sys
import os
import glob

def check_file(file_path):
    print(f"\n{'='*60}")
    print(f"🔎 DIAGNÓSTICO PARA: {os.path.basename(file_path)}")
    print(f"{'='*60}")

    # 1. CARGA CRUDA
    try:
        df = pd.read_parquet(file_path)
    except Exception as e:
        print(f"❌ Error fatal leyendo el archivo: {e}")
        return

    total_rows = len(df)
    print(f"1. Filas Totales en Parquet: {total_rows}")

    if total_rows == 0:
        print("⚠️  El archivo está vacío.")
        return

    # 2. BUSQUEDA DE IDs
    # AMIGA Infill suelen ser IDs >= 100000
    # Standard suelen ser < 100000
    
    infill_raw = df[df['sdId'] >= 100000]
    denso_raw = df[(df['sdId'] >= 90000) & (df['sdId'] < 100000)]
    otros_raw = df[df['sdId'] < 90000]

    print(f"\n2. Distribución de IDs (Crudos):")
    print(f"   - Infill (>100k):      {len(infill_raw)} filas")
    print(f"   - Anillo UMD (90k):    {len(denso_raw)} filas")
    print(f"   - SD Standard (<90k):  {len(otros_raw)} filas")
    print(f"   - Max ID encontrado:   {df['sdId'].max()}")
    print(f"   - Min ID encontrado:   {df['sdId'].min()}")

    if len(infill_raw) == 0:
        print("\n❌ ALERTA ROJA: No hay ningún ID >= 100000 en el archivo crudo.")
        print("   Revisar pipeline C++ -> Python. ¿Se guardaron los contadores correctos?")
        return

    # 3. EL "EMBUDO" DE FILTROS (¿Dónde mueren?)
    print(f"\n3. Análisis del 'Embudo' de limpieza (Solo Infill):")
    
    # Filtro A: NaNs en Reconstrucción
    # El reporte hace: df.dropna(subset=['logE_REC', 'theta_REC'])
    infill_valid_reco = infill_raw.dropna(subset=['logE_REC', 'theta_REC'])
    n_dropped_reco = len(infill_raw) - len(infill_valid_reco)
    
    print(f"   A. Filtro Reco (logE/Theta existen):")
    print(f"      - Sobreviven: {len(infill_valid_reco)}")
    print(f"      - Mueren:     {n_dropped_reco}")
    
    if len(infill_valid_reco) == 0:
        print("      ⚠️  TODOS los eventos Infill tienen logE_REC o theta_REC como NaN.")
        print("      (Posible causa: Eventos de muy baja energía que no reconstruyen SD)")
        return

    # Filtro B: Status del Módulo
    # El reporte hace: module_status.isin(['candidate', 'saturated'])
    # Nota: A veces 'rejected' se usa, pero en v7 pusimos candidate/saturated
    candidates = infill_valid_reco[infill_valid_reco['module_status'] == 'candidate']
    saturated = infill_valid_reco[infill_valid_reco['module_status'] == 'saturated']
    rejected = infill_valid_reco[infill_valid_reco['module_status'] == 'rejected']
    others = infill_valid_reco[~infill_valid_reco['module_status'].isin(['candidate', 'saturated', 'rejected'])]

    print(f"\n   B. Filtro Status Módulo (sobre los que tienen Reco):")
    print(f"      - Candidate: {len(candidates)}")
    print(f"      - Saturated: {len(saturated)}")
    print(f"      - Rejected:  {len(rejected)} (Estos se ignoran en el reporte actual)")
    print(f"      - Otros:     {len(others)}")
    
    valid_final = len(candidates) + len(saturated)
    print(f"\n   ✅ TOTAL DISPONIBLE PARA REPORTE: {valid_final}")

    # 4. CHEQUEO DE UNIDADES (Grados vs Radianes)
    # Esto causó el crash anterior
    print(f"\n4. Chequeo de Unidades Angulares (Phi Euler):")
    max_val = infill_raw['phi_plane_euler'].abs().max()
    print(f"   - Valor máximo absoluto: {max_val:.4f}")
    if max_val > 7:
        print("   -> PARECE SER: GRADOS (OK)")
    else:
        print("   -> PARECE SER: RADIANES (OK)")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 debug_data.py <carpeta_o_archivo_parquet>")
        sys.exit(1)
    
    target = sys.argv[1]
    
    if os.path.isdir(target):
        files = glob.glob(os.path.join(target, "*.parquet"))
        files.sort()
        if not files:
            print("No hay parquets en la carpeta.")
        else:
            # Analizamos solo el primero y el último para no spammear
            print(f"Carpeta detectada. Analizando primer archivo...")
            check_file(files[0])
            if len(files) > 1:
                print("\n... (saltando archivos intermedios) ...")
                print("Analizando último archivo...")
                check_file(files[-1])
    else:
        check_file(target)