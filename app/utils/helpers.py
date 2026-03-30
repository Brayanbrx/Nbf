"""
Funciones auxiliares diversas.
"""

from datetime import datetime


def format_precio(precio):
    """Formatear precio a string con 2 decimales."""
    if precio is None:
        return "0.00"
    return f"{float(precio):.2f}"


def format_fecha(fecha):
    """Formatear fecha a string legible."""
    if isinstance(fecha, str):
        return fecha
    if fecha is None:
        return "-"
    return fecha.strftime('%d/%m/%Y %H:%M')


def format_fecha_corta(fecha):
    """Formatear fecha sin hora."""
    if isinstance(fecha, str):
        return fecha
    if fecha is None:
        return "-"
    return fecha.strftime('%d/%m/%Y')
