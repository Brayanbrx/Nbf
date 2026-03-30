# 🔍 Sistema de Filtros Avanzado - NBF Listados

## ✨ Cambios Realizados

Tu aplicación ahora tiene **2 sistemas de filtros independientes pero integrados** que **NO se pierden entre sí**.

---

## 📱 Cómo Funciona

### 1️⃣ **FILTRO RÁPIDO** (Búsqueda Instantánea)

**Ubicación:** Arriba, en el input grande

```
🔍 Buscar: código, nombre, descripción...  [Buscar] [x]
```

**Características:**

- ✅ Busca por **código, nombre o descripción**
- ✅ **Búsqueda automática** después de 800ms de escribir
- ✅ O presiona **Enter** para buscar inmediatamente
- ✅ **Preserva** los filtros de categoría y marca
- ✅ Muestra "💡 Escribe al menos 1 carácter y espera..."

**Ejemplo:**

1. Escribes "zapatilla" en el buscador
2. Esperas 800ms (u presionas Enter)
3. Se buscan productos con "zapatilla" en código, nombre o descripción
4. Los filtros de categoría y marca **SE MANTIENEN ACTIVOS**

---

### 2️⃣ **FILTRO AVANZADO** (Categoría + Marca)

**Ubicación:** Debajo, en el card gris con "⚙️ Filtros Avanzados"

```
📌 Categoría: [Dropdown]
📌 Marca:     [Dropdown]

[✓ Aplicar Filtros] [↻ Resetear]
```

**Características:**

- ✅ Filtra por **Categoría** (una a la vez)
- ✅ Filtra por **Marca** (una a la vez)
- ✅ **Puedes combinar ambos**
- ✅ Necesitas hacer clic en **"Aplicar Filtros"** (no auto-submit)
- ✅ **Preserva** la búsqueda anterior
- ✅ Botón **"Resetear"** para limpiar solo categoría/marca (mantiene búsqueda)

**Ejemplo:**

1. Buscas "nike" en el filtro rápido
2. Luego seleccionas Categoría = "Deportivo" y Marca = "Nike" en filtro avanzado
3. Haces clic **"Aplicar Filtros"**
4. Ves productos con búsqueda "nike" + categoría "Deportivo" + marca "Nike"

---

### 3️⃣ **ETIQUETAS DE FILTROS ACTIVOS**

**Ubicación:** Debajo de los filtros (solo si hay filtros activos)

```
✓ Filtros activos:  [🔍 Búsqueda: "nike"]  [📌 Deportivo]  [🏢 Nike]
```

- ✅ Muestra visualmente qué filtros están aplicados
- ✅ Ayuda a entender los resultados
- ✅ Puedes hacer clic para modificar

---

## 🎯 Casos de Uso

### Caso 1: Buscar solo por código

```
1. Escribe "PROD-001" en el buscador
2. Espera o presiona Enter
3. Resultado: Productos con código "PROD-001"
```

### Caso 2: Filtrar solo por categoría

```
1. Abre "Filtros Avanzados"
2. Selecciona Categoría = "Electrónica"
3. Haz clic "Aplicar Filtros"
4. Resultado: Todos los productos electrónicos
```

### Caso 3: Combinación completa

```
1. Busca "samsung" (🔍 búsqueda)
2. Selecciona Categoría = "Electrónica"
3. Selecciona Marca = "Samsung"
4. Haz clic "Aplicar Filtros"
5. Resultado: Productos Samsung en categoría Electrónica con "samsung" en datos
```

### Caso 4: Cambiar búsqueda manteniendo filtros

```
1. Tienes filtros: "samsung" + "Electrónica" + "Samsung"
2. Cambias búsqueda a "lg" (overwrite automático)
3. Los filtros de categoría y marca SE MANTIENEN
4. Resultado: Productos LG en categoría Electrónica
```

### Caso 5: Limpiar solo un tipo de filtro

```
1. Haz clic en Resetear
2. Se limpian categoría y marca
3. La búsqueda SE MANTIENE
4. O haz clic en [x] para limpiar TODO
```

---

## 🔧 Detalles Técnicos

### Frontend (JavaScript)

```javascript
FilterSystem = {
  searchTimeout: 800ms, // Debounce

  // Maneja búsqueda automática
  debounceSearch(input),

  // Preserva otros filtros
  applyFilter(filterName, filterValue),

  // Limpia todo o parcial
  clearAllFilters(),
  clearFilter(filterName)
}
```

**Ubicación:** `app/static/js/app.js` (línea ~150)

### Backend (Flask)

```python
@public_bp.route('/catalogo')
def catalogo():
    pagina = request.args.get('pagina', 1, type=int)
    busqueda = request.args.get('busqueda', '', type=str)
    id_categoria = request.args.get('categoria', None, type=int)
    id_marca = request.args.get('marca', None, type=int)

    filtros = {}
    if busqueda: filtros['busqueda'] = busqueda
    if id_categoria: filtros['id_categoria'] = id_categoria
    if id_marca: filtros['id_marca'] = id_marca
```

**Ubicación:** `app/blueprints/public/routes.py` (línea ~33)

### CSS

```css
.quick-search-form {
} /* Búsqueda bonita */
.advanced-filters {
} /* Card filtros avanzados */
.active-filters {
} /* Badges visibles */
```

**Ubicación:** `app/static/css/app.css` (línea ~130)

---

## 📊 URL Examples

**Solo búsqueda:**

```
/catalogo?busqueda=nike
```

**Solo categoría:**

```
/catalogo?categoria=5
```

**Búsqueda + Categoría + Marca:**

```
/catalogo?busqueda=nike&categoria=5&marca=3
```

**Sin filtros:**

```
/catalogo
```

---

## 🎨 Styling

| Elemento          | Color         | Efecto                   |
| ----------------- | ------------- | ------------------------ |
| Búsqueda          | Azul Primary  | Input gris + botón azul  |
| Filtros Avanzados | Gris 200      | Card con gradiente suave |
| Badge Búsqueda    | Azul Primary  | `bg-primary`             |
| Badge Categoría   | Azul Info     | `bg-info`                |
| Badge Marca       | Verde Success | `bg-success`             |

---

## 📱 Responsive

| Tamaño               | Vista                    | Comportamiento |
| -------------------- | ------------------------ | -------------- |
| **Desktop** (>768px) | 2 columnas (Cat + Marca) | Normal         |
| **Tablet** (768px)   | 2 columnas stacked       | Normal         |
| **Móvil** (480px)    | Full width               | Optimizado     |

---

## ✅ Features Implementados

- ✅ Filtro rápido con debounce (800ms)
- ✅ Filtro avanzado con múltiples campos
- ✅ Preservación de filtros entre requests
- ✅ Badges visuales de filtros activos
- ✅ Botones de reset independiente
- ✅ Responsive en móvil
- ✅ Sin JavaScript requerido (fallback HTML)
- ✅ Soporte keyboard (Enter en búsqueda)

---

## 🚀 Uso en Producción

Tu aplicación está lista. Los filtros funcionan:

- ✅ En Render (con Flask)
- ✅ En móvil (responsive)
- ✅ Sin dependencias adicionales
- ✅ Con performance optimizado

**¡Los usuarios pueden filtrar exactamente como necesitan! 🎉**

---

## 🔄 Diferencia con el Sistema Anterior

| Aspecto                 | Antes                    | Ahora                   |
| ----------------------- | ------------------------ | ----------------------- |
| **Filtros simultáneos** | ❌ Se pisaban            | ✅ Coexisten            |
| **Búsqueda**            | Input simple             | 🚀 Con debounce         |
| **Categoría + Marca**   | Dropdowns independientes | 📌 Formulario unificado |
| **Visual**              | Basico                   | 💎 Cards + Badges       |
| **Mobile**              | Confuso                  | 📱 Optimizado           |
| **UX**                  | Frustante                | 😊 Intuitivo            |
