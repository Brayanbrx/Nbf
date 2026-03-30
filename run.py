#!/usr/bin/env python
"""
Script de entrada para la aplicación Flask.
Ejecutar con: python run.py
"""

import os
import sys
from app import create_app, db
from app.models import Usuario, Categoria, Marca, Producto
from flask_migrate import Migrate

# Crear la aplicación
app = create_app(os.getenv('FLASK_ENV', 'development'))

# Configurar migraciones
migrate = Migrate(app, db)

@app.shell_context_processor
def make_shell_context():
    """Contexto para flask shell."""
    return {
        'db': db,
        'Usuario': Usuario,
        'Categoria': Categoria,
        'Marca': Marca,
        'Producto': Producto,
    }

@app.cli.command()
def create_admin():
    """Comando para crear un usuario admin inicial con password hasheado correctamente."""
    import getpass
    from werkzeug.security import generate_password_hash
    from app.repositories.usuario_repository import UsuarioRepository
    
    print("=" * 50)
    print("Crear Usuario Admin")
    print("=" * 50)
    
    nombre = input("Nombre: ").strip()
    if not nombre:
        print("❌ El nombre no puede estar vacío.")
        return
    
    email = input("Email: ").strip()
    if not email or '@' not in email:
        print("❌ Email inválido.")
        return
    
    # Verificar si ya existe
    repo = UsuarioRepository(db)
    existente = repo.obtener_por_email(email)
    if existente:
        print(f"❌ El usuario con email '{email}' ya existe.")
        return
    
    # Pedir password
    password = getpass.getpass("Password: ")
    password_confirm = getpass.getpass("Confirmar Password: ")
    
    if password != password_confirm:
        print("❌ Las contraseñas no coinciden.")
        return
    
    if len(password) < 6:
        print("❌ La contraseña debe tener al menos 6 caracteres.")
        return
    
    # Crear usuario
    password_hash = generate_password_hash(password)
    usuario = Usuario(
        nombre=nombre,
        email=email,
        password_hash=password_hash,
        rol='ADMIN',
        activo=True
    )
    
    try:
        db.session.add(usuario)
        db.session.commit()
        print(f"✅ Administrador '{nombre}' ({email}) creado correctamente.")
        print("   Puedes iniciar sesión en /login")
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error al crear usuario: {str(e)}")

@app.cli.command()
def init_db():
    """Inicializar la base de datos con tablas predeterminadas."""
    print("Inicializando base de datos...")
    db.create_all()
    print("✅ Base de datos inicializada.")

if __name__ == '__main__':
    # Obtener puerto de variable de entorno (para Render)
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    
    print(f"🚀 Iniciando aplicación en puerto {port}...")
    print(f"   http://localhost:{port}")
    print(f"   http://localhost:{port}/admin  (Panel admin)")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
