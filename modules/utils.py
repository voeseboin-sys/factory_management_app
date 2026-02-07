"""
Utility Functions - Factory Management App
Funciones utilitarias para la aplicación
"""

import os
import sys
import re
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from pathlib import Path

# Detectar plataforma
IS_ANDROID = hasattr(sys, 'getandroidapilevel')


def get_app_directory() -> str:
    """
    Obtiene el directorio base de la aplicación.
    En Android usa el almacenamiento de la app.
    """
    if IS_ANDROID:
        from android.storage import app_storage_path
        return app_storage_path()
    else:
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def ensure_directory(path: str) -> str:
    """Asegura que un directorio exista, lo crea si no existe"""
    os.makedirs(path, exist_ok=True)
    return path


def format_number(num: int or float, decimals: int = 0) -> str:
    """Formatea un número con separadores de miles"""
    if decimals > 0:
        return f"{num:,.{decimals}f}"
    return f"{num:,}"


def format_currency(amount: float, symbol: str = "$") -> str:
    """Formatea un monto como moneda"""
    return f"{symbol}{amount:,.2f}"


def format_datetime(dt: datetime or str, format_str: str = "%d/%m/%Y %H:%M") -> str:
    """Formatea una fecha/hora"""
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))
        except:
            return dt
    return dt.strftime(format_str)


def format_date(date: datetime or str, format_str: str = "%d/%m/%Y") -> str:
    """Formatea una fecha"""
    return format_datetime(date, format_str)


def format_time(time: datetime or str, format_str: str = "%H:%M") -> str:
    """Formatea una hora"""
    return format_datetime(time, format_str)


def get_relative_time(dt: datetime or str) -> str:
    """Retorna tiempo relativo (hace X minutos, etc.)"""
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))
        except:
            return str(dt)
    
    now = datetime.now()
    diff = now - dt
    
    seconds = diff.total_seconds()
    
    if seconds < 60:
        return "hace un momento"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"hace {minutes} minuto{'s' if minutes > 1 else ''}"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f"hace {hours} hora{'s' if hours > 1 else ''}"
    elif seconds < 604800:
        days = int(seconds / 86400)
        return f"hace {days} día{'s' if days > 1 else ''}"
    else:
        return format_date(dt)


def validate_email(email: str) -> bool:
    """Valida un correo electrónico"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_phone(phone: str) -> bool:
    """Valida un número de teléfono"""
    # Remover espacios, guiones y paréntesis
    cleaned = re.sub(r'[\s\-\(\)]', '', phone)
    # Validar que tenga entre 8 y 15 dígitos
    return cleaned.isdigit() and 8 <= len(cleaned) <= 15


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """Trunca un texto a una longitud máxima"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def slugify(text: str) -> str:
    """Convierte un texto a formato slug (URL-friendly)"""
    # Convertir a minúsculas
    text = text.lower()
    # Remover caracteres especiales
    text = re.sub(r'[^\w\s-]', '', text)
    # Reemplazar espacios con guiones
    text = re.sub(r'[-\s]+', '-', text)
    # Remover guiones al inicio y final
    return text.strip('-')


def generate_id(prefix: str = "", length: int = 8) -> str:
    """Genera un ID único"""
    import random
    import string
    
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
    
    if prefix:
        return f"{prefix}-{timestamp}-{random_str}"
    return f"{timestamp}-{random_str}"


def generate_order_number() -> str:
    """Genera un número de orden de trabajo"""
    year = datetime.now().strftime('%Y')
    sequence = datetime.now().strftime('%m%d%H%M%S')
    return f"WO-{year}-{sequence}"


def calculate_efficiency(produced: int, target: int) -> float:
    """Calcula el porcentaje de eficiencia"""
    if target <= 0:
        return 0.0
    return min(100.0, (produced / target) * 100)


def calculate_defect_rate(total: int, defects: int) -> float:
    """Calcula la tasa de defectos"""
    if total <= 0:
        return 0.0
    return (defects / total) * 100


def get_status_color(status: str) -> str:
    """Retorna el color correspondiente a un estado"""
    colors = {
        'pending': '#FF9800',      # Naranja
        'in_progress': '#2196F3',  # Azul
        'completed': '#4CAF50',    # Verde
        'cancelled': '#F44336',    # Rojo
        'on_hold': '#9E9E9E',      # Gris
        'active': '#4CAF50',       # Verde
        'inactive': '#F44336',     # Rojo
        'maintenance': '#FF9800',  # Naranja
    }
    return colors.get(status.lower(), '#9E9E9E')


def get_priority_color(priority: str) -> str:
    """Retorna el color correspondiente a una prioridad"""
    colors = {
        'low': '#4CAF50',      # Verde
        'normal': '#2196F3',   # Azul
        'high': '#FF9800',     # Naranja
        'urgent': '#F44336',   # Rojo
        'critical': '#9C27B0', # Púrpura
    }
    return colors.get(priority.lower(), '#9E9E9E')


def bytes_to_human(size_bytes: int) -> str:
    """Convierte bytes a formato human-readable"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    
    return f"{s} {size_names[i]}"


def parse_boolean(value: Any) -> bool:
    """Parsea un valor a booleano"""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ('true', '1', 'yes', 'on', 'si', 'sí')
    if isinstance(value, (int, float)):
        return value != 0
    return bool(value)


def safe_get(dictionary: Dict, key: str, default: Any = None) -> Any:
    """Obtiene un valor de un diccionario de forma segura"""
    if dictionary is None:
        return default
    return dictionary.get(key, default)


def chunk_list(lst: List, chunk_size: int) -> List[List]:
    """Divide una lista en chunks de tamaño especificado"""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def flatten_list(nested_list: List) -> List:
    """Aplana una lista anidada"""
    result = []
    for item in nested_list:
        if isinstance(item, list):
            result.extend(flatten_list(item))
        else:
            result.append(item)
    return result


def unique_list(lst: List) -> List:
    """Retorna una lista con elementos únicos manteniendo el orden"""
    seen = set()
    result = []
    for item in lst:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


class AppLogger:
    """Logger simple para la aplicación"""
    
    LEVELS = {
        'DEBUG': 0,
        'INFO': 1,
        'WARNING': 2,
        'ERROR': 3,
        'CRITICAL': 4
    }
    
    def __init__(self, level: str = 'INFO'):
        self.level = self.LEVELS.get(level.upper(), 1)
    
    def _log(self, level: str, message: str, *args):
        if self.LEVELS.get(level, 0) >= self.level:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            formatted_msg = message % args if args else message
            print(f"[{timestamp}] [{level}] {formatted_msg}")
    
    def debug(self, message: str, *args):
        self._log('DEBUG', message, *args)
    
    def info(self, message: str, *args):
        self._log('INFO', message, *args)
    
    def warning(self, message: str, *args):
        self._log('WARNING', message, *args)
    
    def error(self, message: str, *args):
        self._log('ERROR', message, *args)
    
    def critical(self, message: str, *args):
        self._log('CRITICAL', message, *args)


# Instancia global del logger
logger = AppLogger('INFO')


# Constantes de la aplicación
class AppConstants:
    """Constantes de la aplicación"""
    
    APP_NAME = "Factory Manager Pro"
    APP_VERSION = "2.0.1"
    APP_AUTHOR = "Factory Manager Team"
    
    # Roles de usuario
    ROLE_ADMIN = "admin"
    ROLE_OPERATOR = "operator"
    ROLE_SUPERVISOR = "supervisor"
    ROLE_MAINTENANCE = "maintenance"
    
    # Estados de producción
    STATUS_PENDING = "pending"
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_COMPLETED = "completed"
    STATUS_CANCELLED = "cancelled"
    
    # Prioridades
    PRIORITY_LOW = "low"
    PRIORITY_NORMAL = "normal"
    PRIORITY_HIGH = "high"
    PRIORITY_URGENT = "urgent"
    
    # Tipos de mantenimiento
    MAINTENANCE_PREVENTIVE = "preventive"
    MAINTENANCE_CORRECTIVE = "corrective"
    MAINTENANCE_PREDICTIVE = "predictive"
    
    # Tipos de movimiento de inventario
    MOVEMENT_IN = "in"
    MOVEMENT_OUT = "out"
    MOVEMENT_ADJUSTMENT = "adjustment"
    MOVEMENT_TRANSFER = "transfer"
