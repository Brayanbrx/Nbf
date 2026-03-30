# Proyecto NBF Listados - Estructura Completa

## Árbol del Proyecto

```
nbf-listados/
│
├── 📁 app/                                 # Paquete principal de la aplicación
│   ├── __init__.py                        # App Factory - crea la aplicación Flask
│   ├── config.py                          # Configuración (Dev/Prod/Test)
│   ├── extensions.py                      # Extensiones inicializadas (db, login_mgr, csrf)
│   │
│   ├── 📁 models/                         # Modelos SQLAlchemy
│   │   └── __init__.py                    # Usuario, Categoria, Marca, Producto, HistorialEdicion
│   │
│   ├── 📁 forms/                          # Formularios WTForms
│   │   ├── __init__.py
│   │   ├── auth_forms.py                  # FormularioLogin
│   │   ├── categoria_forms.py             # FormularioCategoria
│   │   ├── marca_forms.py                 # FormularioMarca
│   │   └── producto_forms.py              # FormularioProducto
│   │
│   ├── 📁 repositories/                   # Data Access Layer
│   │   ├── __init__.py
│   │   ├── usuario_repository.py          # Operaciones CRUD Usuario
│   │   ├── categoria_repository.py        # Operaciones CRUD Categoria
│   │   ├── marca_repository.py            # Operaciones CRUD Marca
│   │   └── producto_repository.py         # Operaciones CRUD Producto con búsqueda
│   │
│   ├── 📁 services/                       # Business Logic Layer
│   │   ├── __init__.py
│   │   ├── auth_service.py                # Lógica autenticación
│   │   ├── categoria_service.py           # Lógica categorías
│   │   ├── marca_service.py               # Lógica marcas
│   │   └── producto_service.py            # Lógica productos
│   │
│   ├── 📁 blueprints/                     # Rutas modularizadas
│   │   ├── public/                        # Catálogo público
│   │   │   ├── __init__.py
│   │   │   └── routes.py                  # GET / /catalogo /catalogo/producto/<id>
│   │   ├── auth/                          # Autenticación
│   │   │   ├── __init__.py
│   │   │   └── routes.py                  # GET/POST /auth/login /auth/logout
│   │   └── admin/                         # Panel administrativo
│   │       ├── __init__.py
│   │       └── routes.py                  # GET/POST /admin/* (CRUD completo)
│   │
│   ├── 📁 utils/                          # Utilidades
│   │   ├── __init__.py
│   │   ├── decorators.py                  # @admin_required, @editor_required
│   │   ├── helpers.py                     # format_precio, format_fecha, etc
│   │   └── security.py                    # hash_password, verify_password
│   │
│   ├── 📁 templates/                      # Plantillas Jinja2
│   │   ├── base.html                      # Plantilla base con navbar y footer
│   │   ├── partials/                      # Componentes reutilizables
│   │   │   ├── navbar.html                # Barra de navegación
│   │   │   ├── footer.html                # Pie de página
│   │   │   ├── flash_messages.html        # Alertas
│   │   │   └── confirm_modal.html         # Modal de confirmación
│   │   ├── public/                        # Templates catálogo público
│   │   │   ├── home.html                  # Página de inicio
│   │   │   ├── catalogo.html              # Catálogo con búsqueda
│   │   │   └── producto_detalle.html      # Detalle producto
│   │   ├── auth/                          # Templates autenticación
│   │   │   └── login.html                 # Formulario login
│   │   └── admin/                         # Templates panel admin
│   │       ├── dashboard.html             # Dashboard
│   │       ├── productos/
│   │       │   ├── listado.html           # Tabla productos con filtros
│   │       │   └── formulario.html        # Crear/editar producto
│   │       ├── categorias/
│   │       │   ├── listado.html           # Tabla categorías
│   │       │   └── formulario.html        # Crear/editar categoría
│   │       └── marcas/
│   │           ├── listado.html           # Tabla marcas
│   │           └── formulario.html        # Crear/editar marca
│   │
│   └── 📁 static/                         # Archivos estáticos
│       ├── css/
│       │   └── app.css                    # CSS personalizado (colores, hover, tablas, etc)
│       ├── js/
│       │   └── app.js                     # JavaScript personalizado (utilidades, modales)
│       └── img/                           # Imágenes (logos, etc) - vacío inicialmente
│
├── 📁 migrations/                         # Migraciones Alembic (vacío inicialmente)
│   └── .gitkeep                           # Placeholder
│
├── 📁 tests/                              # Tests (vacío inicialmente)
│   ├── __init__.py
│   └── conftest.py                        # Fixture para tests
│
├── run.py                                 # Punto de entrada principal
├── requirements.txt                       # Dependencias Python
├── Dockerfile                             # Configuración Docker para Render
├── render.yaml                            # Configuración deployment Render
├── .env.example                           # Ejemplo variables de entorno
├── .gitignore                             # Archivos a ignorar en Git
├── DATABASE_SETUP.sql                     # Script para crear BD desde cero
├── QUICK_START.md                         # Guía de inicio rápido
├── README.md                              # Documentación completa
└── PROJECT_STRUCTURE.md                   # Este archivo
```

---

## Componentes por Capas

### 1️⃣ PRESENTACIÓN (Templates + Estáticos)

- HTML5 con Jinja2
- Bootstrap 5 (CDN)
- CSS personalizado
- JavaScript
- Responsive design

### 2️⃣ CONTROL (Blueprints/Routes)

- Public blueprint (catálogo)
- Auth blueprint (login/logout)
- Admin blueprint (CRUD)
- Decoradores de seguridad

### 3️⃣ NEGOCIO (Services)

- AuthService
- ProductoService
- CategoriaService
- MarcaService
- Validaciones de negocio

### 4️⃣ DATOS (Repositories + Models)

- Models: SQLAlchemy ORM
- Repositories: Acceso a datos
- Queries optimizadas
- Búsquedas y filtros

### 5️⃣ INFRAESTRUCTURA

- Config.py (configuración por entorno)
- Extensions.py (db, login_manager, csrf)
- Dockerfile (containerización)
- render.yaml (deployment)

---

## Patrones Utilizados

✅ **MVC/Modular**: Models, Views (Templates), Controllers (Routes)
✅ **App Factory**: Creación flexible de la app
✅ **Blueprints**: Rutas organizadas por módulo
✅ **Repositories**: Capa de acceso a datos
✅ **Services**: Lógica de negocio separada
✅ **Decorators**: Control de acceso (@admin_required)
✅ **Forms**: Validación con WTForms
✅ **Context Processors**: Variables globales en templates
✅ **Flash Messages**: Retroalimentación al usuario

---

## Características Implementadas

### Catálogo Público

- ✅ Homepage atractiva
- ✅ Búsqueda por código/nombre
- ✅ Filtros por categoría y marca
- ✅ Paginación automática
- ✅ Detalle de producto
- ✅ Imágenes con placeholder
- ✅ Precios condicionados (mostrar solo si está habilitado)
- ✅ Responsive (mobile, tablet, desktop)

### Panel Admin

- ✅ Autenticación por sesión
- ✅ Dashboard con estadísticas
- ✅ CRUD Productos (crear, leer, editar, eliminar)
- ✅ CRUD Categorías
- ✅ CRUD Marcas
- ✅ Búsqueda y filtros avanzados
- ✅ Control de visibilidad pública
- ✅ Gestión de precios (paquete, docena, caja)
- ✅ Controlador de unidades
- ✅ Confirmaciones de eliminación
- ✅ Flash messages visuales
- ✅ Tablas HTML estilizadas
- ✅ Formularios con validación server-side

### Seguridad

- ✅ Contraseños hasheados (Werkzeug)
- ✅ Protección CSRF (Flask-WTF)
- ✅ Autenticación con Flask-Login
- ✅ Control de acceso por rol (@admin_required)
- ✅ Sesiones seguras
- ✅ Sin credenciales en texto plano

### Base de Datos

- ✅ SQL Server (local o Somee)
- ✅ SQLAlchemy ORM
- ✅ Migraciones con Alembic
- ✅ Constraints de integridad
- ✅ Índices para performance
- ✅ Auditoría de cambios (HistorialEdicion)
- ✅ Relaciones FK correctas

### Despliegue

- ✅ Docker para Render
- ✅ Gunicorn como servidor
- ✅ Soporte para variables de entorno
- ✅ ODBC Driver 18 incluido
- ✅ Multi-stage build optimizado

---

## Dependencias Principales

```
Flask==3.0.0
Flask-SQLAlchemy==3.1.1
Flask-Migrate==4.0.5
Flask-Login==0.6.3
Flask-WTF==1.2.1
WTForms==3.1.1
python-dotenv==1.0.0
pyodbc==5.1.0
gunicorn==21.2.0
Werkzeug==3.0.1
```

---

## Tamaño Aproximado

- **Backend**: ~50 KB de código Python
- **Frontend**: ~30 KB de HTML/CSS/JS
- **Templates**: ~25 KB Jinja2
- **Total**: ~105 KB (muy manejable)

---

## Próximos Pasos

1. **Instalar dependencias**: `pip install -r requirements.txt`
2. **Crear BD**: Ejecutar `DATABASE_SETUP.sql` en SQL Server
3. **Configurar .env**: Copiar `.env.example` a `.env` y editar
4. **Crear admin**: `flask create-admin`
5. **Ejecutar**: `python run.py`
6. **Acceder**: http://localhost:5000

---

## Escalabilidad Futura

Este proyecto está diseñado para crecer:

- 📊 Agregar más vistas/reportes
- 🔍 Búsqueda avanzada (full-text search)
- 📊 Analytics y dashboards
- 🛒 E-commerce (carrito, checkout)
- 📱 API REST (Flask-RESTful)
- 🔔 Notificaciones (Flask-Mail)
- 💾 Caché (Redis)
- 🔐 OAuth2/SSO
- 📚 Documentación API (Swagger)

---

## Notas Finales

✨ Este es un proyecto **production-ready** que respeta:

- Clean Code
- SOLID principles
- DRY (Don't Repeat Yourself)
- Flask best practices
- SQL Server best practices
- Bootstrap accessibility
- Responsive web design

🚀 **¡Listo para usar en producción con Render!**
