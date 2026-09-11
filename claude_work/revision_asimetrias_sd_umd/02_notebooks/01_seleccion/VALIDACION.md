# Verificación de la entrega

- Notebook ejecutado de principio a fin: **28 celdas de código**, sin errores.
- **26 celdas explicativas** intercaladas; fuente .py y .ipynb coinciden.
- **7 figuras** visibles dentro del notebook, además de sus PNG y PDF en exports/.
- Coeficientes de las cuatro bandas e intervalos bootstrap recalculados desde filas:
  coinciden con el control anterior de veinte archivos.
- No se cargaron coeficientes desde JSON para construir los gráficos del notebook.
- Tiempo registrado del recorrido principal: 18.85 segundos;
  no es una garantía de tiempo en otras máquinas o cargas del servidor.
- Run All con relectura ROOT desactivada; utiliza pandas y un hilo numérico.
- Prueba ROOT separada: 200 filas recuperadas de nuevo, incluyendo
  **105 sin entrada SD reconstruida**. Sus conteos,
  condición de presencia y coordenadas coinciden con la caché.
- El piloto ROOT es parcial. Las advertencias reales de esquema del diccionario
  están explicadas en el notebook y README; no se certifica todo el contenido ADST.

La coincidencia valida esta reproducción y la disponibilidad de esos registros;
no demuestra por sí sola un fallo del algoritmo de reconstrucción ni aísla la
causa electromagnética del efecto de selección.
