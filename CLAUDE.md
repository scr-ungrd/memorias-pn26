# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Repositorio: https://github.com/scr-ungrd/memorias-pn26  
Organización: Subdirección para el Conocimiento del Riesgo, UNGRD (Colombia)

## Comandos principales

```bash
# Vista previa con recarga automática
quarto preview

# Compilar libro completo (HTML + PDF)
quarto render

# Compilar solo un capítulo
quarto render sesiones-paralelas/sp-01/index.qmd

# Publicar en GitHub Pages
quarto publish gh-pages

# Extraer ID de Google Drive de un archivo local sincronizado
xattr -l "ruta/al/archivo.pptx" | grep 'com.google.drivefs.item-id'

# Leer contenido de una nota conceptual .docx
pandoc "ruta/al/archivo.docx" -t plain

# Leer nota conceptual en PDF
pdftotext "ruta/al/archivo.pdf" -

# Extraer contenido útil de un .docx de escenario-en-vivo (aparece tras esa línea)
pandoc "archivo.docx" -t plain | sed -n '/No se aceptan/,$ p'
```

## Arquitectura del libro

Quarto book con salidas HTML (cosmo + brand + custom.scss) y PDF (lualatex / scrreprt). La estructura de capítulos se declara completamente en `_quarto.yml` — cualquier nuevo `index.qmd` debe registrarse allí bajo su `part:` correspondiente.

### Secciones del libro

```
plenarias/                  p-01 … p-05        (5 sesiones)
sesiones-tematicas/         st-01…06           (6 sesiones)
sesiones-paralelas/         sp-01…25, 27…38   (35 sesiones, faltan sp-03/26/36)
sesiones-especiales/        se-01…10            (10 sesiones)
laboratorios-de-aprendizaje/ la-01…10           (10 sesiones)
dialogos-de-alto-nivel/     an-01…03           (3 sesiones)
escenarios-en-vivo/         ev-01…16, ev-18…46  (45 sesiones, sin ev-17)
posters/                    pt-01                (1 sesión, prefijo: pt)
```

Prefijo para los IDs de tabla: quitar guiones del prefijo de carpeta (`sp01`, `ev01`, `pt01`, etc.).

Cada sección tiene un `index.qmd` de portada (solo `title:` en frontmatter) y subcarpetas `{prefijo}-{NN}/index.qmd` para cada sesión.

## Plantilla de sesión

Cada `index.qmd` tiene exactamente tres bloques. Ver `sesiones-paralelas/sp-01/index.qmd` como referencia canónica.

La estructura de H2 de cada `index.qmd` de sesión es fija: `## Nota conceptual` → `## Diapositivas de la sesión` → `## Video de la sesión`.

**1. Nota conceptual** — dos tablas Markdown en divs con ID:
- `#tabla-{id}-info`: tabla de dos columnas sin encabezado (datos de organización)
- `#tabla-{id}-desc`: tabla con encabezado `Sección | Descripción`
- El `id` sigue el patrón del prefijo de carpeta sin guión: `p01`, `sp01`, etc.

**2. Bloque `<style>`** — inline, pinta la primera fila de `-info` y el `thead` de `-desc` en `#00ACA8`:

```html
<style>
#tabla-{id}-info tbody tr:first-child {
  background-color: #00ACA8;
  color: #fff;
}
#tabla-{id}-desc thead tr {
  background-color: #00ACA8;
  color: #fff;
}
</style>
```

En plenarias el `<style>` va suelto (no dentro de ` ```{=html} ` ), en sp-01 va dentro de un bloque ` ```{=html} `. Ambas formas funcionan; usar la forma suelta (sin bloque raw) para las sesiones nuevas para consistencia con plenarias.

**3. Diapositivas** — sección `## Diapositivas de la sesión` con iframe de Google Drive o Google Slides. Si no hay PPTX, escribir `*Diapositivas no disponibles.*` en lugar del iframe:

```html
<!-- Archivo Drive (PPTX subido) -->
<iframe src="https://drive.google.com/file/d/{FILE_ID}/preview" width="100%" height="480" allowfullscreen></iframe>

<!-- Google Slides nativo -->
<iframe src="https://docs.google.com/presentation/d/{PRESENTATION_ID}/embed?start=false&loop=false&delayms=3000" width="100%" height="480" allowfullscreen></iframe>
```

**4. Video** — sección `## Video de la sesión` con iframe de YouTube con timestamp en segundos:

```html
<iframe src="https://www.youtube.com/embed/{VIDEO_ID}?start={SECONDS}" width="100%" height="480" allowfullscreen></iframe>
```

## Plantilla escenarios-en-vivo

Las sesiones `ev-NN` tienen una estructura diferente al resto: **sin tablas de nota conceptual**. La mayoría incluye `## Diapositivas de la sesión` con iframe cuando el ponente subió diapositivas. La base es frontmatter YAML + párrafo de perfil; el iframe es opcional pero frecuente (presente en ~33 de 46 ev).

```yaml
---
title: Título del trabajo
author:
- name: Nombre Apellido
  affiliations:
    - name: Institución, Ciudad, País
  corresponding: true
  email: correo@ejemplo.com
keywords:
- Palabra clave 1
abstract: |
  Párrafo 1...

  Párrafo 2...
categories:
- Comunidades de aprendizaje y participación   # exactamente 1 de las 4 abajo
- Datos, modelación, IA, innovación social y herramientas digitales  # eje transversal (si aplica)
---

**Perfil quién presenta el trabajo:** Texto del perfil...
```

**Área Temática Principal** (exactamente 1, texto exacto):
- `Comunidades de aprendizaje y participación`
- `Planeación y ordenamiento que incorpora la GRD`
- `Territorialización y financiamiento de la GRD`
- `Preparación y recuperación oportuna`

**Ejes transversales** (opcionales, máximo 1):
- `Adaptación al cambio climático desde el enfoque de Eco-Reducción (Eco-RRD)`
- `Datos, modelación, IA, innovación social y herramientas digitales`

Cuando no hay .docx disponible (o el archivo tiene solo Lorem ipsum): usar frontmatter minimal con solo `title` y `author`, sin abstract/keywords/categories/perfil.

**ev-17 no existe** — era duplicado de ev-05, fue omitido deliberadamente.

## Plantilla posters

Las sesiones `pt-NN` siguen la misma plantilla que escenarios-en-vivo (frontmatter YAML + párrafo de perfil, sin tablas de nota conceptual), pero con `## Poster` en lugar de `## Diapositivas de la sesión`:

```html
## Poster

<iframe src="https://drive.google.com/file/d/{FILE_ID}/preview" width="100%" height="700" allowfullscreen></iframe>
```

## Errores conocidos / YAML

- Los títulos con comillas dobles en el frontmatter YAML rompen el renderizado. Reemplazar `"` por `'` en los valores de `title:`. Ejemplo: `'Caribbean "Sea" Framework'` → `"Caribbean 'Sea' Framework"` o simplemente eliminar las comillas internas.

## Mapeos especiales

### Laboratorios: número agenda ≠ número carpeta Drive

| ID libro | Carpeta Drive |
|---|---|
| la-03 | LA11-MINIGUALDAD (DISCAPACIDAD LAB3) |
| la-07 | LA03-MUSEO-BOLSILLO-MAGMA |
| la-10 | LA13-SISTEMA-NAL-INFORM-UNGRD |

Siempre usar el número de la agenda oficial para el ID del libro.

### Sesiones especiales: SE06

`se-06` en el libro corresponde a la carpeta Drive `SE07-ANIMALES-UNGRD`, no a `SE06-GRD-AGROPECUARIO-FAO`.

### Sesiones no incluidas (no estaban en agenda PDF v4)

SP3-CAMPESINOS, SP26, SP36, SP39, SP40, SP42, SP44, ST07-EMERGENCIAS-MOVILIDAD, ST08-MOVILIDAD-HUMANA

## Nota: SE04-MINTRANSPORTE y SP26

SE04-MINTRANSPORTE sí está incluida (como `se-04`). Su propia nota conceptual la referencia internamente como "Sesión Paralela 26" — probablemente fue reclasificada de sesión paralela a sesión especial en algún momento del proceso, lo que explica por qué SP26 aparece como faltante en `sesiones-paralelas/`.

## Paleta de colores y tipografía

| Token | Valor | Uso |
|---|---|---|
| Teal | `#00ACA8` | Encabezados de tablas de nota conceptual |
| Azul oscuro | `#003a70` | Item activo en sidebar y TOC |
| Naranja-rojo | `#e54d23` | Hover en navegación |

Fuentes (declaradas en `custom.scss`): Roboto (cuerpo), Lato (títulos, `font-weight: 600`), Fira Code (código).

## Flujo para agregar una sesión nueva

1. Crear carpeta `{sección}/{prefijo}-{NN}/` con `index.qmd` siguiendo la plantilla sp-01.
2. Registrar el capítulo en `_quarto.yml` bajo el `part:` correspondiente.
3. Obtener el FILE_ID de Drive con `xattr` y el timestamp de YouTube desde el video correspondiente.
4. Si hay nota conceptual en `.docx`, extraer con `pandoc … -t plain` y adaptar las tablas Markdown.

## Fuentes de contenido en Google Drive

- **Notas conceptuales (.docx) y diapositivas (.pptx):** `Shared drives/PLATAFORMA NACIONAL GRD 2026/11-SESIONES-AGENDA-PUNTOS-FOCALES/{sección}/{carpeta-sesión}/` — el archivo PPTX tiene "PANTALLA" en el nombre.
- **Resúmenes de escenarios-en-vivo (.docx):** `Shared drives/PLATAFORMA NACIONAL GRD 2026/9-ESCENARIOS-EN-VIVO/3-ARCHIVOS-SESIONES/Resumenes-postulados/` (raíz y subcarpeta `pdf/docx/`)
