#!/bin/bash

# ==============================================================================
# Script de Automatización de Reportes - Tesis Licenciatura
# Autor: Lautaro Silva Pizzi
# ==============================================================================

# --- 1. CONFIGURACIÓN ---

# Script Individual (que corre por carpeta)
PYTHON_SCRIPT="generar_reporte_v8.py"

# Script Global (que corre al final)
GLOBAL_SCRIPT="generar_reporte_GLOBAL.py"

# Ruta base donde están tus carpetas de parquets
DATA_BASE_DIR="/home/lsilva/Github/ADST_Alexey_module_v9"

# Patrón para encontrar las carpetas
DIR_PATTERN="parquet_*"

# Carpeta para guardar logs
LOG_DIR="logs_reportes"
mkdir -p "$LOG_DIR"

# --- 2. VALIDACIONES ---

if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "Error: No encuentro el script individual '$PYTHON_SCRIPT'."
    exit 1
fi

if [ ! -f "$GLOBAL_SCRIPT" ]; then
    echo "Error: No encuentro el script global '$GLOBAL_SCRIPT'."
    exit 1
fi

if [ ! -d "$DATA_BASE_DIR" ]; then
    echo "Error: La ruta de datos '$DATA_BASE_DIR' no existe."
    exit 1
fi

# --- 3. EJECUCIÓN MASIVA (INDIVIDUALES) ---

echo "========================================================"
echo " FASE 1: Generación de Reportes Individuales"
echo " Fecha: $(date)"
echo "========================================================"
echo ""

count=0
total=$(find "$DATA_BASE_DIR" -maxdepth 1 -name "$DIR_PATTERN" -type d | wc -l)

for folder in "$DATA_BASE_DIR"/$DIR_PATTERN; do
    if [ -d "$folder" ]; then
        ((count++))
        folder_name=$(basename "$folder")
        
        echo "[$count/$total] Procesando: $folder_name ..."
        
        parquet_count=$(ls "$folder"/*.parquet 2>/dev/null | wc -l)
        
        if [ "$parquet_count" -eq 0 ]; then
            echo "Salteando: No hay archivos .parquet en $folder_name"
            continue
        fi

        log_file="$LOG_DIR/${folder_name}.log"
        
        start_time=$(date +%s)
        python3 "$PYTHON_SCRIPT" "$folder" > "$log_file" 2>&1
        exit_code=$?
        end_time=$(date +%s)
        duration=$((end_time - start_time))

        if [ $exit_code -eq 0 ]; then
            echo "Éxito ($duration seg). Log: $log_file"
        else
            echo "ERROR. Revisar log: $log_file"
        fi
    fi
done

# --- 4. EJECUCIÓN FINAL (GLOBAL) ---

echo ""
echo "========================================================"
echo " FASE 2: Generación de Reporte Global"
echo "========================================================"

echo "Esperando 2 segundos para asegurar cierre de archivos..."
sleep 2

echo "Ejecutando: $GLOBAL_SCRIPT"
# Ejecutamos el global y mostramos la salida en pantalla (no log) para ver errores de una
python3 "$GLOBAL_SCRIPT"

echo ""
echo "========================================================"
echo " Procesamiento Completo Finalizado."
echo "========================================================"