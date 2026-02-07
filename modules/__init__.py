"""
Factory Management App - Modules Package
"""

from .database import DatabaseManager
from .pdf_generator import PDFGenerator
from .utils import (
    AppConstants, AppLogger, logger, IS_ANDROID,
    get_app_directory, ensure_directory, format_number,
    format_currency, format_datetime, format_date, format_time,
    get_relative_time, validate_email, validate_phone,
    truncate_text, slugify, generate_id, generate_order_number,
    calculate_efficiency, calculate_defect_rate,
    get_status_color, get_priority_color, bytes_to_human
)

__all__ = [
    'DatabaseManager', 
    'PDFGenerator',
    'AppConstants',
    'AppLogger',
    'logger',
    'IS_ANDROID'
]
