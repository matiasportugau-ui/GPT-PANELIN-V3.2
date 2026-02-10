# Panelin - Guía Completa de Knowledge Base
**Versión:** 3.0
**Fecha:** 2026-02-07
**KB Version:** 7.0

---

## Estructura de Knowledge Base

Esta guía describe todos los archivos que Panelin necesita en su Knowledge Base, su propósito, prioridad y cómo deben usarse.

---

## Jerarquía de Archivos (Orden de Prioridad)

### NIVEL 1 - MASTER (Fuente de Verdad Absoluta)

**Propósito**: Fuente autorizada para precios de paneles, fórmulas y especificaciones técnicas.

#### Archivos:
- **`BMC_Base_Conocimiento_GPT-2.json`** (PRIMARIO - OBLIGATORIO)
- **`bromyros_pricing_master.json`** (base completa de productos BROMYROS)

**Contenido:**
- Productos completos (ISODEC, ISOPANEL, ISOROOF, ISOWALL, ISOFRIG, HM_RUBBER)
- Precios validados de Shopify
- Fórmulas de cotización exactas (incluyendo v6: tortugas_pvc, arandelas_carrocero, fijaciones_perfileria)
- Especificaciones técnicas (autoportancia, coeficientes térmicos, resistencia térmica)
- Reglas de negocio
- Correcciones técnicas validadas
- Precios de referencia rápida para accesorios principales

**Cuándo usar:**
- **SIEMPRE** para precios de paneles
- **SIEMPRE** para fórmulas de cálculo
- **SIEMPRE** para especificaciones técnicas
- **SIEMPRE** para validación de autoportancia

**Regla de oro**: Si hay conflicto con otros archivos, Nivel 1 gana.

---

### NIVEL 1.2 - ACCESORIOS (Precios reales)

**Propósito**: Catálogo completo de accesorios con precios IVA incluido.

#### Archivo:
- **`accessories_catalog.json`** (70+ ítems con precios reales)

**Contenido:**
- Goteros frontales y laterales por espesor
- Babetas (adosar, empotrar, laterales)
- Cumbreras, canalones, perfiles U
- Fijaciones (varillas, tuercas, tacos, arandelas, tortugas PVC)
- Selladores (silicona, cinta butilo)
- Índices por SKU, tipo, compatibilidad y uso

**Cuándo usar:**
- Para obtener precios unitarios de accesorios en cotizaciones
- Para seleccionar el accesorio correcto según espesor y sistema
- Para consultar disponibilidad por proveedor (BROMYROS, MONTFRIO, BECAM)

---

### NIVEL 1.3 - REGLAS BOM (Bill of Materials)

**Propósito**: Reglas paramétricas para calcular cantidades de accesorios por sistema constructivo.

#### Archivo:
- **`bom_rules.json`** (6 sistemas constructivos)

**Contenido:**
- Fórmulas parametrizadas por sistema (techo_isoroof_3g, techo_isodec_eps, techo_isodec_pir, pared_isopanel_eps, pared_isowall_pir, pared_isofrig_pir)
- Tabla de autoportancia unificada
- Mapeo de SKU por espesor
- Kits de fijación detallados (metal, hormigón, madera)
- Ejemplo de cálculo completo paso a paso

**Cuándo usar:**
- Para determinar qué accesorios necesita cada sistema
- Para calcular cantidades usando fórmulas paramétricas
- Para validar autoportancia (tabla unificada)
- Para seleccionar kit de fijación según tipo de estructura

---

### NIVEL 1.5 - PRICING OPTIMIZADO

**Propósito**: Búsquedas rápidas de precios por SKU, familia o tipo.

#### Archivo:
- **`bromyros_pricing_gpt_optimized.json`**

**Contenido:**
- Índice optimizado de productos BROMYROS
- Búsqueda por SKU, familia, subfamilia

**Cuándo usar:**
- Para lookups rápidos cuando se conoce el SKU
- Ver `GPT_INSTRUCTIONS_PRICING.md` para instrucciones detalladas de uso

---

### NIVEL 1.6 - CATÁLOGO (Descripciones e imágenes)

**Propósito**: Información de productos para presentación al cliente.

#### Archivos:
- **`shopify_catalog_v1.json`** (descripciones, variantes, imágenes)
- **`shopify_catalog_index_v1.csv`** (índice para búsquedas rápidas via Code Interpreter)

**Cuándo usar:**
- Para descripciones de productos
- Para imágenes de referencia
- **NO usar para precios** (usar Nivel 1 para precios)

---

### NIVEL 2 - VALIDACIÓN (Cross-Reference)

**Propósito**: Validación cruzada y detección de inconsistencias.

#### Archivo:
- **`BMC_Base_Unificada_v4.json`**

**Contenido:**
- Productos validados contra 31 presupuestos reales
- Fórmulas validadas
- Precios de referencia
- Notas sobre validación

**Cuándo usar:**
- **SOLO** para cross-reference
- **SOLO** para detectar inconsistencias
- **NO** usar para respuestas directas
- Si detectas diferencia, reportarla pero usar Nivel 1

---

### NIVEL 3 - DINÁMICO (Tiempo Real)

**Propósito**: Verificación de precios actualizados y estado de stock.

#### Archivo:
- **`panelin_truth_bmcuruguay_web_only_v2.json`**

**Contenido:**
- Snapshot público de la web
- Precios actualizados (como texto de referencia)
- Estado de stock
- Catálogo web

**Cuándo usar:**
- Verificar precios actualizados (pero validar contra Nivel 1)
- Consultar estado de stock
- **Siempre verificar contra Nivel 1** antes de usar

---

### NIVEL 4 - SOPORTE (Contexto y Reglas)

**Propósito**: Información complementaria, reglas técnicas y workflows.

#### Archivos:

1. **`panelin_context_consolidacion_sin_backend.md`**
   - SOP completo de consolidación, checkpoints y gestión de contexto
   - Comandos: `/estado`, `/checkpoint`, `/consolidar`

2. **`Aleros -2.rtf`**
   - Reglas técnicas específicas de voladizos y aleros
   - Nota: Si OpenAI no acepta .rtf, convertir a .txt o .md primero

3. **`PANELIN_QUOTATION_PROCESS.md`**
   - Proceso de cotización en 5 fases obligatorias

4. **`PANELIN_TRAINING_GUIDE.md`**
   - Guía de entrenamiento y evaluación de ventas

5. **`GPT_INSTRUCTIONS_PRICING.md`**
   - Instrucciones de lookup rápido de precios BROMYROS

6. **`GPT_PDF_INSTRUCTIONS.md`**
   - Instrucciones para generación de PDFs profesionales

7. **`GPT_OPTIMIZATION_ANALYSIS.md`**
   - Análisis de configuración y plan de mejoras

---

## Lista Completa de Archivos Necesarios

### Archivos Obligatorios (Nivel 1):
- [ ] `BMC_Base_Conocimiento_GPT-2.json` (PRIMARIO)
- [ ] `bromyros_pricing_master.json` (BROMYROS completo)

### Archivos de Accesorios y BOM (Nivel 1.2-1.3):
- [ ] `accessories_catalog.json` (70+ accesorios con precios)
- [ ] `bom_rules.json` (reglas BOM paramétricas)

### Archivos de Pricing y Catálogo (Nivel 1.5-1.6):
- [ ] `bromyros_pricing_gpt_optimized.json` (lookup rápido)
- [ ] `shopify_catalog_v1.json` (descripciones e imágenes)
- [ ] `shopify_catalog_index_v1.csv` (índice CSV)

### Archivos de Validación (Nivel 2):
- [ ] `BMC_Base_Unificada_v4.json`

### Archivos Dinámicos (Nivel 3):
- [ ] `panelin_truth_bmcuruguay_web_only_v2.json`

### Archivos de Soporte (Nivel 4):
- [ ] `panelin_context_consolidacion_sin_backend.md`
- [ ] `Aleros -2.rtf`
- [ ] `PANELIN_QUOTATION_PROCESS.md`
- [ ] `PANELIN_TRAINING_GUIDE.md`
- [ ] `GPT_INSTRUCTIONS_PRICING.md`
- [ ] `GPT_PDF_INSTRUCTIONS.md`
- [ ] `GPT_OPTIMIZATION_ANALYSIS.md`

---

## Cómo Usar Cada Archivo

### Para Precios de Paneles:
1. **PRIMERO**: Consultar `BMC_Base_Conocimiento_GPT-2.json`
2. **SEGUNDO**: Verificar en `panelin_truth_bmcuruguay_web_only_v2.json` si hay actualización
3. **NUNCA**: Usar `BMC_Base_Unificada_v4.json` como fuente primaria

### Para Precios de Accesorios:
1. **PRIMERO**: Consultar `accessories_catalog.json` para el precio exacto del ítem
2. **SEGUNDO**: Usar `BMC_Base_Conocimiento_GPT-2.json` → `precios_accesorios_referencia` para precios rápidos de referencia
3. **SIEMPRE**: Seleccionar el accesorio correcto según espesor y sistema (ver `bom_rules.json`)

### Para Fórmulas y BOM:
1. **FÓRMULAS**: Usar `formulas_cotizacion` en `BMC_Base_Conocimiento_GPT-2.json`
2. **BOM PARAMÉTRICO**: Usar `bom_rules.json` para cantidades por sistema constructivo
3. **NUNCA**: Inventar o modificar fórmulas

### Para Validación Técnica (Autoportancia):
1. **PRIMERO**: Consultar `bom_rules.json` → `autoportancia.tablas`
2. **TAMBIÉN**: `BMC_Base_Conocimiento_GPT-2.json` → `products` → `espesores` → `autoportancia`
3. **VALIDAR**: Luz del cliente vs autoportancia del panel
4. **SI NO CUMPLE**: Sugerir espesor mayor o apoyo adicional

### Para Comandos SOP:
1. **CONSULTAR**: `panelin_context_consolidacion_sin_backend.md` para estructura completa
2. **EJECUTAR**: Comandos según especificación en ese archivo

### Para Reglas Técnicas Específicas:
1. **ALEROS**: Consultar `Aleros -2.rtf`
2. **WORKFLOWS**: Consultar `panelin_context_consolidacion_sin_backend.md`

---

## Reglas Críticas

### Regla #1: Source of Truth
- **Nivel 1 siempre gana** en caso de conflicto
- **Nunca inventar datos** que no estén en KB
- **Si no está en KB**, decir "No tengo esa información"

### Regla #2: Prioridad de Consulta
1. Consultar Nivel 1 primero (paneles) o Nivel 1.2 (accesorios)
2. Si no está, verificar Nivel 2 (pero reportar)
3. Si no está, verificar Nivel 3 (pero validar contra Nivel 1)
4. Si no está, consultar Nivel 4 para contexto
5. Si no está en ningún lado, decir "No tengo esa información"

### Regla #3: Validación Cruzada
- Usar Nivel 2 para detectar inconsistencias
- Reportar diferencias pero usar Nivel 1
- Nunca usar Nivel 2 para respuesta directa

### Regla #4: Actualización
- Nivel 3 puede tener precios más recientes
- Siempre validar contra Nivel 1 antes de usar
- Si hay diferencia, usar Nivel 1 y reportar

---

## Estructura de Datos Esperada

### En `BMC_Base_Conocimiento_GPT-2.json`:
```json
{
  "meta": {
    "version": "6.0-Unified",
    "fecha": "2026-01-27"
  },
  "products": {
    "ISODEC_EPS": {
      "espesores": {
        "100": {
          "autoportancia": 5.5,
          "precio": 46.07,
          "coeficiente_termico": 0.035,
          "resistencia_termica": 2.86
        }
      }
    }
  },
  "formulas_cotizacion": {
    "calculo_apoyos": "ROUNDUP((LARGO / AUTOPORTANCIA) + 1)",
    "puntos_fijacion_techo": "ROUNDUP(((CANTIDAD * APOYOS) * 2) + (LARGO * 2 / 2.5))",
    "tortugas_pvc": "PUNTOS * 1",
    "arandelas_carrocero": "PUNTOS * 1",
    "fijaciones_perfileria": "ROUNDUP(METROS_LINEALES_TOTALES / 0.30)"
  },
  "precios_accesorios_referencia": {
    "varilla_3_8": 3.81,
    "tuerca_3_8": 0.15,
    "taco_3_8": 1.17
  }
}
```

---

## Proceso de Actualización

Cuando se actualiza un archivo en Knowledge Base:

1. **Eliminar** el archivo antiguo del GPT
2. **Subir** el nuevo archivo
3. **Esperar** unos minutos para reindexación
4. **Probar** que funcione correctamente
5. **Verificar** que Nivel 1 sigue siendo la fuente primaria

---

## Checklist de Verificación

Antes de considerar la Knowledge Base completa:

- [ ] `BMC_Base_Conocimiento_GPT-2.json` está subido (Nivel 1)
- [ ] `bromyros_pricing_master.json` está subido (Nivel 1)
- [ ] `accessories_catalog.json` está subido (Nivel 1.2)
- [ ] `bom_rules.json` está subido (Nivel 1.3)
- [ ] `bromyros_pricing_gpt_optimized.json` está subido (Nivel 1.5)
- [ ] `shopify_catalog_v1.json` está subido (Nivel 1.6)
- [ ] `shopify_catalog_index_v1.csv` está subido (Nivel 1.6)
- [ ] `BMC_Base_Unificada_v4.json` está subido (Nivel 2)
- [ ] `panelin_truth_bmcuruguay_web_only_v2.json` está subido (Nivel 3)
- [ ] `panelin_context_consolidacion_sin_backend.md` está subido (Nivel 4)
- [ ] `Aleros -2.rtf` o equivalente está subido (Nivel 4)
- [ ] Todos los archivos de soporte MD están subidos (Nivel 4)
- [ ] Instrucciones del sistema referencian correctamente la jerarquía
- [ ] Panelin lee correctamente Nivel 1 para precios de paneles
- [ ] Panelin lee correctamente Nivel 1.2 para precios de accesorios
- [ ] Panelin usa correctamente las fórmulas del JSON
- [ ] Panelin detecta y reporta conflictos correctamente

---

## Troubleshooting

### Problema: Panelin no lee el archivo correcto
**Solución**:
- Verificar que `BMC_Base_Conocimiento_GPT-2.json` esté subido primero
- Reforzar en instrucciones: "SIEMPRE leer BMC_Base_Conocimiento_GPT-2.json primero"

### Problema: Panelin inventa precios
**Solución**:
- Agregar guardrail más estricto en instrucciones
- Verificar que Nivel 1 esté completo
- Probar con consulta simple: "¿Cuánto cuesta ISODEC 100mm?"

### Problema: Fórmulas incorrectas
**Solución**:
- Verificar que use fórmulas de `formulas_cotizacion` del JSON
- Agregar ejemplo en instrucciones
- Probar con caso conocido y comparar resultado

### Problema: Precios de accesorios incorrectos
**Solución**:
- Verificar que `accessories_catalog.json` esté subido
- Confirmar que el GPT consulta este archivo para accesorios (no solo `precios_accesorios_referencia`)
- Probar: "¿Cuánto cuesta una varilla roscada 3/8?"

### Problema: BOM incompleto
**Solución**:
- Verificar que `bom_rules.json` esté subido
- Confirmar que el GPT selecciona el sistema correcto (techo_isodec_eps, pared_isopanel_eps, etc.)
- Probar con cotización completa y verificar que incluya todos los accesorios

---

**Última actualización**: 2026-02-07
**Versión**: 3.0 (KB v7.0)
