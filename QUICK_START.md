# 🚀 Inicio Rápido - NBF Listados

## En 5 Minutos

### 1️⃣ Preparar Base de Datos

```bash
# Opción A: Ejecutar el script SQL
# Abrir SQL Server Management Studio
# File > Open > Seleccionar DATABASE_SETUP.sql
# Ejecutar (F5)

# Opción B: Manual
CREATE DATABASE NBF_Listados;
```

### 2️⃣ Clonar Proyecto

```bash
cd c:\Users\braya\Desktop\prueba\nbf-listados
```

### 3️⃣ Entorno Virtual

```bash
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

### 4️⃣ Configurar .env

```bash
copy .env.example .env
# Editar .env con tus datos
```

Contenido mínimo:

```
FLASK_ENV=development
SECRET_KEY=tu-clave-super-secreta
DB_SERVER=localhost
DB_USER=sa
DB_PASSWORD=tu_contraseña_sql
```

### 5️⃣ Crear Admin

```bash
flask create-admin
# Ingresa nombre, email, password
```

### 6️⃣ ¡Listo!

```bash
python run.py
```

Abre el navegador:

- **Inicio**: http://localhost:5000
- **Catálogo**: http://localhost:5000/catalogo
- **Admin**: http://localhost:5000/admin

---

## Credenciales de Prueba

Usa las que creaste con `flask create-admin`

---

## Errores Comunes

| Error                 | Solución                                   |
| --------------------- | ------------------------------------------ |
| ODBC Driver not found | Instalar from Microsoft                    |
| DB connection failed  | Verificar SQL Server está corriendo        |
| Table already exists  | Eliminar BD y crear nueva                  |
| ModuleNotFoundError   | Ejecutar `pip install -r requirements.txt` |

---

**¡Listo para empezar! 🎉**
