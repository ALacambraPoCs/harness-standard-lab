---
runbook: rollback-pages
servicio: sitio en GitHub Pages (workflow despliegue-pages)
propietario: "@<persona o equipo responsable>"
revisado: AAAA-MM-DD
---

# Rollback del sitio en GitHub Pages

<!-- harness:cuando -->
## Cuándo usarlo
- Hay una issue «Despliegue fallido …» que dice que el rollback **no** se completó, o que no había versión anterior.
- El sitio sirve una versión verificada pero **funcionalmente rota** (el despliegue automático no lo detecta: solo comprueba qué SHA se sirve).

<!-- harness:pasos -->
## Pasos
1. **Elegir la versión buena.** En la rama por defecto, `git log --first-parent --oneline` y elegir el último commit de merge que funcionaba. Para comprobar lo que se fusionó en él: `harness audit <sha>`.
2. **Lanzar el rollback.** *Actions → despliegue-pages → Run workflow*. En «Use workflow from», la **rama por defecto** (desde otra rama lo bloquean el workflow y el environment). En `sha`, el SHA **completo** (40 caracteres).
3. **Esperar el run en verde.** El job `verificar` comprueba que `<url>/version.txt` es ese SHA.
4. **Registrar.** Comentar la issue con el enlace al run y cerrarla. Si el fallo viene de un PR, abrir una tarea para corregirlo: no se revierte el commit en la rama por defecto desde aquí.

<!-- harness:verificacion -->
## Verificación
- `curl -s <url>/version.txt` devuelve el SHA elegido. La caché de Pages puede tardar hasta 10 minutos.
- El run de `despliegue-pages` está en verde y su resumen incluye la auditoría.

<!-- harness:escalado -->
## Escalado
- Si el run no puede desplegar (permisos, environment, Pages desactivado): responsable de plataforma del repositorio.
- Si ninguna versión de la historia funciona: desactivar Pages en *Settings → Pages* y avisar a quien use el sitio.

<!-- harness:permisos -->
## Permisos necesarios
Lanzar workflows (Actions, escritura) en el repositorio. **No** hace falta acceso de administración ni a secretos. Un agente no debe lanzar este procedimiento: su token no tiene Actions ni Deployments (D-069).
