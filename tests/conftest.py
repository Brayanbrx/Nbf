# Plantilla base para tests conftest.py

import pytest
from app import create_app, db
from app.models import Usuario, Categoria, Marca, Producto


@pytest.fixture
def app():
    """Crear y configurar una nueva app para testing."""
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Cliente de prueba."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Runner para comandos CLI."""
    return app.test_cli_runner()
