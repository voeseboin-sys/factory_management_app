"""
Configuration File - Factory Manager Pro
Configuración centralizada de la aplicación
"""

import os

# ============================================
# CONFIGURACIÓN GENERAL
# ============================================

APP_NAME = "Factory Manager Pro"
APP_VERSION = "2.0.1"
APP_AUTHOR = "Factory Manager Team"
APP_DESCRIPTION = "Sistema de Gestión de Producción Industrial"

# ============================================
# CONFIGURACIÓN DE BASE DE DATOS
# ============================================

DB_NAME = "factory_manager.db"
DB_VERSION = 1

# ============================================
# CONFIGURACIÓN DE UI
# ============================================

# Orientación de la pantalla
ORIENTATION = "landscape"

# Tema por defecto
DEFAULT_THEME = "Light"
DEFAULT_PRIMARY_PALETTE = "Indigo"
DEFAULT_ACCENT_PALETTE = "Amber"

# Colores personalizados
COLORS = {
    'primary': '#3F51B5',
    'primary_dark': '#303F9F',
    'accent': '#FFC107',
    'success': '#4CAF50',
    'warning': '#FF9800',
    'error': '#F44336',
    'info': '#2196F3',
}

# ============================================
# CONFIGURACIÓN DE PDF
# ============================================

PDF_CONFIG = {
    'font_family': 'Arial',
    'font_size_normal': 11,
    'font_size_title': 16,
    'font_size_header': 12,
    'page_format': 'A4',
    'margin_top': 20,
    'margin_bottom': 20,
    'margin_left': 15,
    'margin_right': 15,
}

# ============================================
# CONFIGURACIÓN DE REPORTES
# ============================================

REPORTS_CONFIG = {
    'max_reports_to_keep': 100,
    'auto_cleanup_days': 30,
    'default_report_prefix': 'report',
}

# ============================================
# CONFIGURACIÓN DE AUTENTICACIÓN
# ============================================

# Usuario por defecto (cambiar en producción)
DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_PASSWORD = "admin"

# Sesión
SESSION_TIMEOUT_MINUTES = 30

# ============================================
# CONFIGURACIÓN DE PRODUCCIÓN
# ============================================

PRODUCTION_CONFIG = {
    'default_shift_start': '06:00',
    'default_shift_end': '14:00',
    'max_defect_rate': 5.0,  # Porcentaje máximo de defectos aceptable
    'target_efficiency': 85.0,  # Eficiencia objetivo
}

# ============================================
# CONFIGURACIÓN DE NOTIFICACIONES
# ============================================

NOTIFICATIONS_CONFIG = {
    'enabled': True,
    'low_stock_alert': True,
    'production_complete': True,
    'maintenance_due': True,
    'defect_rate_high': True,
}

# ============================================
# CONFIGURACIÓN DE SINCRONIZACIÓN
# ============================================

SYNC_CONFIG = {
    'auto_sync': False,
    'sync_interval_minutes': 15,
    'server_url': '',  # Configurar en producción
    'api_key': '',     # Configurar en producción
}

# ============================================
# CONFIGURACIÓN DE ANDROID
# ============================================

ANDROID_CONFIG = {
    'package_name': 'com.factorymanager.app',
    'api_target': 33,  # Android 13
    'api_minimum': 26,  # Android 8.0
    'permissions': [
        'INTERNET',
        'WRITE_EXTERNAL_STORAGE',
        'READ_EXTERNAL_STORAGE',
        'MANAGE_EXTERNAL_STORAGE',
        'ACCESS_NETWORK_STATE',
        'WAKE_LOCK',
        'VIBRATE',
    ],
    'architectures': ['arm64-v8a', 'armeabi-v7a'],
}

# ============================================
# FUNCIONES DE CONFIGURACIÓN
# ============================================

def get_config(key: str, default=None):
    """Obtiene un valor de configuración"""
    # Primero buscar en variables de entorno
    env_value = os.getenv(f'FACTORY_MANAGER_{key.upper()}')
    if env_value is not None:
        return env_value
    
    # Luego buscar en este módulo
    return globals().get(key, default)


def is_android():
    """Detecta si estamos ejecutando en Android"""
    import sys
    return hasattr(sys, 'getandroidapilevel')


def get_db_path():
    """Obtiene la ruta de la base de datos según la plataforma"""
    if is_android():
        from android.storage import app_storage_path
        return os.path.join(app_storage_path(), 'databases', DB_NAME)
    else:
        return os.path.join(os.path.dirname(__file__), DB_NAME)


def get_reports_path():
    """Obtiene la ruta de reportes según la plataforma"""
    if is_android():
        from android.storage import app_storage_path
        return os.path.join(app_storage_path(), 'reports')
    else:
        return os.path.join(os.path.dirname(__file__), 'reports')
