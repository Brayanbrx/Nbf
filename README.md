# NBF Listados - Catálogo de Productos

> Aplicación web completa para catálogo público y panel administrativo de productos.
> Stack: Flask + Jinja2 + Bootstrap 5 + SQL Server + Render

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.12%2B-blue)
![Flask](https://img.shields.io/badge/flask-3.0%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

---

## 📋 Tabla de Contenidos

- [Características](#características)
- [Requisitos](#requisitos)
- [Instalación Local](#instalación-local)
- [Configuración](#configuración)
- [Uso](#uso)
- [Despliegue en Render](#despliegue-en-render)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [API/Rutas](#rutas-disponibles)
- [Mejoras Futuras](#mejoras-futuras)

---

## ✨ Características

### Catálogo Público

- ✅ Visualización de productos activos
- ✅ Búsqueda por código, nombre, categoría y marca
- ✅ Filtros dinámicos
- ✅ Paginación optimizada
- ✅ Detalle completo de productos con precios
- ✅ Imágenes con placeholder automático
- ✅ Interfaz responsive (móvil, tablet, desktop)

### Panel Administrativo

- ✅ Autenticación por sesión
- ✅ CRUD completo de productos
- ✅ CRUD de categorías y marcas
- ✅ Control de visibilidad en catálogo público
- ✅ Gestión de precios (paquete, docena, caja)
- ✅ Dashboard con estadísticas
- ✅ Filtros avanzados en listados
- ✅ Confirmación de eliminación
- ✅ Flash messages intuitivos

### Técnicas

- ✅ Arquitectura MVC/modular con blueprints
- ✅ Validaciones de formularios con WTForms
- ✅ ORM SQLAlchemy con migraciones Alembic
- ✅ Autenticación con Flask-Login
- ✅ Protección CSRF con Flask-WTF
- ✅ Bootstrap 5 (CDN) sin build tools
- ✅ Diseño limpio y mantenible
- ✅ Listo para producción con Docker

---

## 📦 Requisitos

### Local

- Python 3.12+
- SQL Server 2019+ (local o Somee)
- pip (gestor de paquetes Python)
- ODBC Driver 17 o 18 para SQL Server

### Producción

- Cuenta en Render (free o pago)
- Cuenta en Somee (para BD en la nube)
- Variables de entorno configuradas

---

## 🚀 Instalación Local

### 1. Clonar/Descargar el Proyecto

```bash
cd c:\Users\braya\Desktop\prueba\nbf-listados
```

### 2. Crear Entorno Virtual

```bash
python -m venv venv
.\venv\Scripts\activate
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno

Copiar `.env.example` a `.env` y editarlo:

```bash
cp .env.example .env
```

Abrir `.env` y configurar:

```
FLASK_ENV=development
SECRET_KEY=tu-clave-muy-segura-aqui

# Base de datos LOCAL
DB_DRIVER=ODBC Driver 17 for SQL Server
DB_SERVER=localhost
DB_PORT=1433
DB_NAME=NBF_Listados
DB_USER=sa
DB_PASSWORD=tu_contraseña_sql_server
```

### 5. Crear Base de Datos en SQL Server

```sql
-- En SQL Server Management Studio o Query:
CREATE DATABASE NBF_Listados;
```

### 6. Inicializar Migraciones

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

O simplemente:

```bash
# Esto crea las tablas automáticamente
flask shell
# En la shell:
>>> db.create_all()
>>> exit()
```

### 7. Crear Admin

```bash
flask create-admin
```

Se pedirá:

- Nombre: Tu Nombre
- Email: tu@email.com
- Password: contraseña_segura

### 8. Ejecutar Aplicación

```bash
python run.py
```

La aplicación estará en:

- **Inicio**: http://localhost:5000
- **Catálogo**: http://localhost:5000/catalogo
- **Admin**: http://localhost:5000/admin
  - Email: `tu@email.com`
  - Password: (la que ingresaste)

---

## ⚙️ Configuración

### Variables de Entorno Disponibles

| Variable      | Valor                         | Descripción                         |
| ------------- | ----------------------------- | ----------------------------------- |
| `FLASK_ENV`   | development/production        | Entorno de ejecución                |
| `SECRET_KEY`  | string                        | Clave secreta (generar con secrets) |
| `DB_DRIVER`   | ODBC Driver 18 for SQL Server | Driver ODBC                         |
| `DB_SERVER`   | localhost                     | Host del servidor SQL               |
| `DB_PORT`     | 1433                          | Puerto SQL Server                   |
| `DB_NAME`     | NBF_Listados                  | Nombre de la base de datos          |
| `DB_USER`     | sa                            | Usuario SQL Server                  |
| `DB_PASSWORD` | xxxx                          | Contraseña SQL Server               |
| `PORT`        | 8000                          | Puerto de la app (Render)           |

### Conectar a Somee (Producción)

1. Registrarse en [Somee.com](https://www.somee.com)
2. Crear base de datos SQL Server
3. Copiar connection string (reemplazar `user` y `password`)
4. En Render, configurar variable `DATABASE_URL` con esa cadena

Ejemplo:

```
DATABASE_URL=mssql+pyodbc://user:password@somee-server.mssql.somee.com/database?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes
```

---

## 💻 Uso

### Catálogo Público

1. Ir a http://localhost:5000/catalogo
2. Usar buscador (código o nombre)
3. Filtrar por categoría o marca
4. Clic en producto para ver detalles
5. Ver precios habilitados (paquete, docena, caja)

### Panel Admin

1. Ir a http://localhost:5000/admin/login
2. Ingresar email y contraseña creados
3. **Dashboard**: Ver estadísticas
4. **Productos**: Crear, editar, eliminar
5. **Categorías**: Gestionar categorías
6. **Marcas**: Gestionar marcas

#### Acciones Admin

- ✏️ **Editar**: Clic en lápiz
- 🗑️ **Eliminar**: Clic en papelera + confirmar
- 👁️ **Visibilidad**: Checkbox en formulario
- 💰 **Precios**: Separados por tipo (paquete/docena/caja)
- 📸 **Imagen**: URL externa
- 🏷️ **Categoría/Marca**: Dropdown (crear antes si es necesario)

---

## 🌐 Despliegue en Render

### Paso 1: Preparar Repositorio Git

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/tu-usuario/tu-repo.git
git push -u origin main
```

### Paso 2: Crear Aplicación en Render

1. Ir a [Render.com](https://render.com)
2. Conectar GitHub
3. Crear nuevo **Web Service**
4. Seleccionar repositorio
5. Configurar:
   - **Name**: nbf-listados
   - **Root Directory**: ./
   - **Runtime**: Docker
   - **Build Command**: dejar vacío (usa Dockerfile)
   - **Start Command**: dejar vacío (usa Dockerfile)

### Paso 3: Configurar Variables de Entorno en Render

En **Environment**:

```
FLASK_ENV=production
SECRET_KEY=[generar con: python -c "import secrets; print(secrets.token_hex(32))"]
DB_DRIVER=ODBC Driver 18 for SQL Server
DB_SERVER=somee-server.mssql.somee.com
DB_PORT=1433
DB_NAME=tu_bd_somee
DB_USER=tu_usuario_somee
DB_PASSWORD=tu_password_somee
```

O usar `DATABASE_URL` si lo prefieres:

```
DATABASE_URL=mssql+pyodbc://usuario:password@servidor/bd?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes&Encrypt=yes
```

### Paso 4: Crear Base de Datos en Somee

1. Registrarse en [Somee.com](https://www.somee.com)
2. Crear BD SQL Server
3. Copiar connection string
4. Usar datos en Render

### Paso 5: Deploy

- Render detecta cambios en `main` automáticamente
- Ver logs en **Logs** (pestaña)
- URL de producción: `https://tu-app.onrender.com`

### Paso 6: Crear Admin en Producción

Una vez desplegado:

```bash
# En terminal (desde Render Shell si está disponible)
# o vía SSH si lo soporta

# Ejecutar comando
flask create-admin
```

O acceder a la shell de Render y ejecutar lo mismo.

---

## 📁 Estructura del Proyecto

```
nbf-listados/
├── app/
│   ├── __init__.py                    # App factory
│   ├── config.py                      # Configuración
│   ├── extensions.py                  # Extensiones (db, login_manager, etc)
│   ├── models/                        # Modelos SQLAlchemy
│   │   └── __init__.py
│   ├── forms/                         # Formularios WTForms
│   ├── repositories/                  # Data Access Layer
│   ├── services/                      # Business Logic Layer
│   ├── blueprints/                    # Rutas modularizadas
│   │   ├── public/                    # Catálogo público
│   │   ├── auth/                      # Autenticación
│   │   └── admin/                     # Panel admin
│   ├── utils/                         # Decoradores y helpers
│   ├── templates/                     # Plantillas Jinja2
│   │   ├── base.html
│   │   ├── public/
│   │   ├── auth/
│   │   ├── admin/
│   │   └── partials/
│   └── static/                        # CSS, JS, imágenes
│       ├── css/
│       ├── js/
│       └── img/
├── migrations/                        # Migraciones Alembic
├── tests/                             # Tests (vacío, listo para agregar)
├── run.py                             # Punto de entrada
├── requirements.txt                   # Dependencias Python
├── Dockerfile                         # Configuración Docker
├── render.yaml                        # Configuración Render
├── .env.example                       # Ejemplo de variables
├── .gitignore                         # Archivos a ignorar
└── README.md                          # Este archivo
```

---

## 🛣️ Rutas Disponibles

### Públicas (sin login)

- `GET /` → Página de inicio
- `GET /catalogo` → Catálogo con búsqueda y filtros
- `GET /catalogo/producto/<id>` → Detalle del producto

### Autenticación

- `GET /auth/login` → Formulario de login
- `POST /auth/login` → Procesar login
- `GET /auth/logout` → Cerrar sesión

### Admin (requieren autenticación)

- `GET /admin` → Dashboard
- `GET /admin/productos` → Listado de productos
- `GET /admin/productos/nuevo` → Crear producto
- `POST /admin/productos/nuevo` → Guardar nuevo producto
- `GET /admin/productos/<id>/editar` → Editar producto
- `POST /admin/productos/<id>/editar` → Guardar cambios
- `POST /admin/productos/<id>/eliminar` → Eliminar producto
- `GET /admin/categorias` → Listado de categorías
- `GET /admin/categorias/nueva` → Crear categoría
- `POST /admin/categorias/nueva` → Guardar categoría
- `GET /admin/categorias/<id>/editar` → Editar categoría
- `POST /admin/categorias/<id>/editar` → Guardar cambios
- `POST /admin/categorias/<id>/eliminar` → Eliminar categoría
- `GET /admin/marcas` → Listado de marcas (ídem categorías)

---

## 🔧 Comandos Útiles

```bash
# Crear admin
flask create-admin

# Inicializar BD
flask init-db

# Shell interactivo
flask shell
    >>> from app.models import *
    >>> db.session.query(Producto).count()
    >>> exit()

# Crear migración
flask db migrate -m "Descripción"

# Aplicar migración
flask db upgrade

# Ver logs
flask shell
    >>> from app.models import Usuario
    >>> Usuario.query.all()

# Eliminar BD (peligroso!)
flask shell
    >>> db.drop_all()
    >>> exit()
```

---

## 🐛 Troubleshooting

### Error: "ODBC Driver not found"

- Windows: Instalar [ODBC Driver 18 from Microsoft](https://learn.microsoft.com/sql/connect/odbc/download-odbc-driver-for-sql-server)
- Linux: `sudo apt install odbc-postgresql` o msodbcsql18

### Error: "Could not connect to database"

- Verificar que SQL Server está corriendo: `Services` (Windows) o `sudo systemctl start mssql-server` (Linux)
- Revisar `.env`: DB_SERVER, DB_USER, DB_PASSWORD correctos
- Probar conexión: usar SSMS o Azure Data Studio

### Error: "Table already exists"

- Puede ocurrir migración duplicada
- Solución: `flask db downgrade` (volver atrás) y luego `flask db upgrade`

### Admin no puede acceder

- Verificar: usuario creado con `flask create-admin`
- Verificar: `Activo = 1` en BD
- Verificar: Rol = 'ADMIN' en BD

---

## 📈 Mejoras Futuras

- [ ] Soporte para múltiples idiomas (i18n)
- [ ] Cargar imágenes directamente (no solo URLs)
- [ ] Rol EDITOR adicional (solo editar productos)
- [ ] Búsqueda avanzada (rango de precios, etc)
- [ ] Exportar productos a Excel/PDF
- [ ] Historial de cambios de productos
- [ ] API REST para integraciones externas
- [ ] Sistema de comentarios/reseñas públicas
- [ ] Carrito de compras (si agrega e-commerce)
- [ ] Notificaciones por email
- [ ] Analytics y estadísticas avanzadas
- [ ] Soporte multimoneda
- [ ] Temas (dark mode, etc)
- [ ] Tests unitarios e integración

---

## 📝 Licencia

MIT License - Libre para usar y modificar.

---

## 👨‍💼 Soporte

Para problemas:

1. Revisar logs en Render o terminal local
2. Verificar variables de entorno
3. Confirmar BD está accesible
4. Ejecutar comandos de troubleshooting arriba

---

**Hecho con ❤️ usando Flask, Jinja2 y Bootstrap 5**

Última actualización: {{ now.strftime('%Y-%m-%d') }}
