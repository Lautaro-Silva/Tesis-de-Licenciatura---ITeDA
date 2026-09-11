# ¿Qué origina la inversión de la asimetría muónica del SD?

Resumen para dirección · Revisión de simulaciones SD–UMD

**Resultado principal.** En la muestra estudiada, exigir que exista una estación SD reconstruida induce la inversión del conteo muónico medio. Al retirar ese requisito, la asimetría SD vuelve a ser positiva. El efecto demostrado es un **sesgo de selección respecto de la población previa a ese requisito**, no una nueva interacción atmosférica ni un fallo demostrado de Offline.

**Qué quedó de la explicación matemática.** Se verificaron la geometría y el cambio de variables de la distribución angular en la formulación corregida, dentro de sus supuestos. La atenuación pasiva y la proyección del flujo radial saliente favorecen temprano; la preferencia angular por la región tardía compite con la dilución espacial. No se sostiene que los muones blandos deban invertir el signo. Estas verificaciones no convierten el modelo aproximado en una predicción cuantitativamente validada.

**Prueba con la simulación.** Se leyeron conteos MC ya guardados en {{files}} archivos ADST de protones SIBYLL 2.3e, incluyendo estaciones que el lector del parquet descartaba por no tener contraparte SD reconstruida. No se ejecutaron nuevas simulaciones. Con geometría MC, 30 ≤ θ < 40°, 1200 ≤ r < 1350 m, doce bins azimutales y el ajuste ponderado del gráfico original, se obtuvo A₁(SD) = **{{sd_before}} antes** y **{{sd_after}} después** del requisito, frente a **{{umd}} para UMD**. A₁ positivo significa exceso temprano. La diferencia SD antes − UMD es {{delta}}, con intervalo bootstrap pareado del 95% [{{low}}, {{high}}]: compatible con cero en esa banda, pero las curvas no coinciden en todo el rango radial.

**Hipótesis física pendiente de aislar.** La mayor contribución electromagnética temprana puede ayudar a retener tanques con pocos muones. Con menor ayuda electromagnética, los tanques tardíos retenidos pueden estar enriquecidos en muones. Así aumenta el promedio tardío **entre estaciones seleccionadas**, sin aumentar el flujo tardío previo a selección. El conteo del UMD no está ligado tan directamente a los muones que producen la señal del tanque asociado; esto podría debilitar el efecto, pero no está demostrado por separado.

**Conclusión defendible para la tesis.** La selección explica la inversión SD en este control. No cierra toda la diferencia con el modelo analítico ni la explicación del UMD. El control conserva los eventos escritos en ADST y las estaciones simuladas disponibles; UMD sigue seleccionado y sus resúmenes ausentes no pueden sustituirse por ceros físicos.

Evidencia reproducible: [comparación directa y figura](02_notebooks/03_sd_vs_umd/comparar_sd_umd.html) · [procedencia y control de selección](02_notebooks/01_seleccion/seleccion_sd_paso_a_paso.html) · [derivación y auditoría](01_fisica/report.html).
