# Capítulo 3 — criterio del borrador

Reemplazo completo propuesto, en español, de `03_fenomenologia.tex`. No se modificó la tesis ni se introdujeron resultados numéricos nuevos. Conserva los dos esquemas, los principales títulos y etiquetas que otros capítulos ya referencian. Las ecuaciones nuevas usan `eq:fen2026:`. El control empírico se remite a `subsec:control_seleccion_sd` del nuevo capítulo 6.

## Qué incorpora y qué corrige

- Conserva la separación presentada en RAFA entre atenuación, proyección y divergencia angular. Retira la afirmación universal de la diapositiva «El observable» según la cual un coeficiente negativo exige un mecanismo adicional: una ADF suficientemente pendiente puede producirlo en principio. La inversión concreta del conteo seleccionado se identifica por el control de selección, no por excluir todas las distribuciones de producción posibles.
- Conserva el signo de proyección para flujo saliente, pero precisa el momento radial firmado y el promedio de flujo. No todos los muones tienen necesariamente `p_r>0`.
- Deriva la ADF normalizada a partir de un espectro transversal **aproximado**, manteniendo `p²/Z(p/Q)` bajo la integral espectral. Distingue momento de energía total y energía en producción de energía al suelo. No reproduce como «predicción validada» las coincidencias numéricas del antiguo modelo sin transporte.
- Explica la compensación del tanque mediante la integral de las cuerdas. Vale por dirección, no sólo como cancelación temprano–tardía. Se limita a fluencia uniforme en la escala del tanque, trazas completas y rendimiento de señal proporcional a longitud. No anula el conteo MC ni la modulación del flujo incidente.
- Corrige la identificación histórica del `+2` de Armbruster/Luce con una apertura de placa: `+2` es dilución inversa cuadrática; la placa introduce otro `+1`; la señal ideal de trazas completas no lo contiene por compensación de cuerdas.
- Introduce la identidad exacta del promedio condicionado. `HasStation` es una condición de presencia de objeto reconstruido, no se presenta como un único umbral de electrónica. El efecto neto de selección está establecido para la muestra controlada; la ayuda EM/enriquecimiento muónico es una interpretación plausible, no una causalidad de disparo ya aislada ni un fallo demostrado de Offline.
- No interpreta un registro UMD ausente como cero físico ni afirma conocer su población anterior a selección.

## Fuentes y precedencia

1. Texto actual `Tesis - Latex/capitulos/03_fenomenologia.tex` y borradores de `kinematic_divergence_explainer_and_thesis_updates/` y `revision_asimetrias_sd_umd/03_borradores_tesis/`: estructura, figuras y argumentos a revisar.
2. `gap_notes_asimetrias_review_v4/kinematic_divergence_math_check.md`: geometría coherente, signos y competencia angular. `sd_umd_synthesis.md` se usa como registro histórico: su promedio espectral y su inferencia de una inversión del flujo no seleccionado fueron superados; no se conservan.
3. `kinematic_divergence_explainer_and_thesis_updates/explainer_kinematic_divergence_simulator.py`, §8, y `spectrum_weighting_correction.html`, §§3–6 y 10: cociente de integrales y normalización dependiente del momento; alcance de la fuente puntual.
4. `revision_asimetrias_sd_umd/01_fisica/report.md`, §§4–5, y `physics_explanation.md`: distinción señal/conteo, significado del bracket, selección y límites de la inferencia UMD. Estos documentos prevalecen sobre las afirmaciones incompatibles de las revisiones anteriores.
5. `presentacion_rafa_2026/presentacion_rafa_2026.tex`, diapositivas de mecanismos y «¿Qué explica la inversión del SD?»: hilo de exposición. La charla no se utiliza como prueba independiente de los resultados.

Referencias científicas utilizadas mediante claves ya existentes: `GAP2000_017` (nota interna), `Cazon2012` (artículo, §§2–3), `Luce_ICRC2021` (actas, §2.2), `Pryke1998`, `BradfieldThesis`, `UMD_Design2016`, `GAP2007_124`, `collaboration_2014`, `Billoir2002`.

Se añade una única clave propuesta, `Armbruster2018`, en la bibliografía complementaria de esta entrega. Metadatos comprobados directamente en las primeras páginas de `Bibliografia/Papers sin citar/GAP2020_066.pdf`: **Lukas Armbruster, Asymmetries of the Lateral Distribution of Particles at the Ground, Bachelor Thesis, KIT, junio de 2018**. El año de la tesis es 2018, aunque circule como GAP-2020-066. Las secciones relevantes son 2.4–2.6, compensación área/cuerda y Ec. (2.33). No se presenta como artículo revisado por pares.

## Comprobaciones y límites

La ADF queda normalizada porque el cambio `u=sin(alpha)` reduce su integral a `k²/Z ∫₀¹ u exp(-ku) du = 1`. Su derivada logarítmica da exactamente `tan²(alpha)+k sin(alpha)`. La expansión `L≈D[1−epsilon cos(phi)]` produce `+2 epsilon` de dilución, `−gamma_ADF epsilon` angular y `+(D/lambda)epsilon` de supervivencia. La placa añade `+epsilon`; la respuesta ideal de trazas completas añade cero. Estas son identidades o aproximaciones explícitas, no ajustes nuevos.

No se trasladaron al capítulo cifras de modelos puntuales ni parámetros de umbral no calibrados. La magnitud y el control empírico de la inversión se documentan en el capítulo 6 con sus muestras y estimadores. La tesis puede conservar la derivación como herramienta de interpretación sin afirmar una predicción absoluta del UMD ni de toda la distribución SD.
